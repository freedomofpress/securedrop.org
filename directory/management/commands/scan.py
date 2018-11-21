from django.core.management import BaseCommand, CommandError

from directory.models import DirectoryEntry
from directory.utils import bulk_scan
from scanner.utils import url_to_domain


class Command(BaseCommand):
    # Adapted from Secure The News https://securethe.news
    help = "Scan one or all SecureDrop landing pages for security"

    def add_arguments(self, parser):
        parser.add_argument(
            'securedrops',
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

    def handle(self, *args, **options):
        if options['securedrops']:
            requested_domains = [url_to_domain(x) for x in options['securedrops']]
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
        else:
            securedrop_pages = DirectoryEntry.objects.all()

        bulk_scan(securedrop_pages)
        self.stdout.write('Scanning complete! Results added to database.')
