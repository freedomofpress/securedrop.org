from django.core.management import BaseCommand, CommandError

from directory.models import DirectoryEntry
from scanner.scanner import bulk_scan
from scanner.utils import url_to_domain


class Command(BaseCommand):
    # Adapted from Secure The News https://securethe.news
    help = "Scan one or all SecureDrop landing pages for security"

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
                "'http://' removed. If unspecified, scan all landing pages in the "
                "directory."
            ),
        )
        filter_group.add_argument('--all', action='store_true')

    def handle(self, *args, **options):
        if options['domains']:
            requested_domains = [url_to_domain(x) for x in options['domains']]
            securedrop_pages = DirectoryEntry.objects.with_domain_annotation()\
                .filter(domain__in=requested_domains)

            # Check that all the domains provided to the command are in the
            # database. If they are not, raise an error.
            retrieved_domains = list(
                securedrop_pages.values_list('domain', flat=True)
            )
            for requested_domain in requested_domains:
                if requested_domain not in retrieved_domains:
                    msg = "Landing page '{}' does not exist".format(
                        'https://{}'.format(requested_domain)
                    )
                    raise CommandError(msg)
        elif options['all']:
            securedrop_pages = DirectoryEntry.objects.all()
        else:
            securedrop_pages = DirectoryEntry.objects.live()

        bulk_scan(securedrop_pages)
        self.stdout.write('Scanning complete! Results added to database.')
