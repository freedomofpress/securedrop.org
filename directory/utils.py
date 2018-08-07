import csv
from io import StringIO
from typing import TYPE_CHECKING

from directory.models.entry import ScanResult

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
