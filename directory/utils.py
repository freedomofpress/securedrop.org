import csv
from io import StringIO
from typing import TYPE_CHECKING

from django.utils import timezone

from directory.models.entry import ScanResult, DirectoryEntry
from scanner.scanner import perform_scan

if TYPE_CHECKING:
    from directory.models.entry import DirectoryEntryQuerySet  # noqa: F401


#: List of field names on DirectoryEntry that should be included in CSV
directory_entry_fields = ['title', 'onion_address', 'added']


#: List of field names on ScanResult that should be included in CSV.
#: This is all fields on the model except 'securedrop' and 'id'
scan_result_fields = list(filter(
    lambda x: x not in ['securedrop', 'id'],
    (f.name for f in ScanResult._meta.get_fields())
))


def scan_csv(entries: 'DirectoryEntryQuerySet') -> str:
    """
    Turn a DirectoryEntryQuerySet into a CSV where each row has details from
    an entry's most recent live scan
    """

    csv_output = StringIO()
    csv_writer = csv.writer(csv_output)

    # Write a header row
    csv_writer.writerow(directory_entry_fields + scan_result_fields)

    for entry in entries:
        # Get field values from DirectoryEntry
        values = [getattr(entry, field) for field in directory_entry_fields]
        try:
            # Add field values from ScanResult
            result = entry.get_live_result()
            values += [getattr(result, field) for field in scan_result_fields]
        except ScanResult.DoesNotExist:
            # If there's no scan result for the entry, swallow the exception
            # and write nothing
            pass
        csv_writer.writerow(values)

    return csv_output.getvalue()


def bulk_scan(entries: 'DirectoryEntryQuerySet') -> None:
    """
    This method takes a queryset and scans the securedrop pages. Unlike the
    scan method that takes a single SecureDrop instance, this method requires
    a DirectoryEntryQueryset of SecureDrop instances that are in the database
    and always commits the results back to the database.
    """

    # Ensure that we have the domain annotation present
    entries = entries.with_domain_annotation()

    results_to_be_written = []
    for entry in entries:
        current_result = ScanResult(**perform_scan(entry.landing_page_url))

        # This is usually handled by Result.save, but since we're doing a
        # bulk save, we need to do it here
        current_result.securedrop = entry

        # Before we save, let's get the most recent scan before saving
        try:
            prior_result = entry.results.latest()
        except ScanResult.DoesNotExist:
            results_to_be_written.append(current_result)
            continue

        if prior_result.is_equal_to(current_result):
            # Then let's not waste a row in the database
            prior_result.result_last_seen = timezone.now()
            prior_result.save()
        else:
            # Then let's add this new scan result to the database
            results_to_be_written.append(current_result)

    # Write new results to the db in a batch
    return ScanResult.objects.bulk_create(results_to_be_written)


def scan(entry: DirectoryEntry, commit=False) -> ScanResult:
    """
    Scan a single site. This method accepts a DirectoryEntry instance which
    may or may not be saved to the database. You can optionally pass True for
    the commit argument, which will save the result to the database. In that
    case, the passed DirectoryEntry *must* already be in the database.
    """
    result = ScanResult(**perform_scan(entry.landing_page_url))

    if commit:
        result.save()

    return result
