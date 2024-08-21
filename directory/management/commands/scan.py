from django.core.management import BaseCommand, CommandError

from directory.models import DirectoryEntry
from scanner.scanner import bulk_scan
from scanner.utils import url_to_domain


class Command(BaseCommand):
    # Adapted from Secure The News https://securethe.news
    help = (
        "Scan one or all SecureDrop landing pages for security.  By "
        "default, scans all published directory entries and skips "
        "unpublished ones."
    )

    def add_arguments(self, parser):
        filter_group = parser.add_mutually_exclusive_group()

        filter_group.add_argument(
            '--domains',
            nargs='*',
            type=str,
            default='',
            help=(
                "Specify one or more domain names of securedrop landing pages "
                " to scan. Specify the domain name with the 'https://' or "
                "'http://' removed.  Directory entries not matching this domain "
                "will not be scanned."
            ),
        )
        filter_group.add_argument(
            '--all',
            action='store_true',
            help='Scan all directory entries, including unpublished pages.',
        )

    def handle(self, *args, **options):
        if options['domains']:
            requested_domains = set([url_to_domain(x) for x in options['domains']])
            securedrop_pages = DirectoryEntry.objects.with_domain_annotation()\
                .filter(domain__in=requested_domains)

            # Check that all the domains provided to the command are in the
            # database. If they are not, raise an error.
            retrieved_domains = set(
                securedrop_pages.values_list('domain', flat=True)
            )

            if diff := requested_domains.difference(retrieved_domains):
                domains = ', '.join(diff)
                raise CommandError(
                    f"No landing pages matching: {domains}\nScan aborted."
                )
        elif options['all']:
            securedrop_pages = DirectoryEntry.objects.all()
        else:
            securedrop_pages = DirectoryEntry.objects.live()

        bulk_scan(securedrop_pages)
        self.stdout.write('Scanning complete! Results added to database.')
