from django.core.management import BaseCommand, CommandError

from directory.models import Securedrop
from directory.landing_page.scanner import bulk_scan


class Command(BaseCommand):
    # Adapted from Secure The News https://securethe.news
    help = "Scan one or all SecureDrop landing pages for security"

    def add_arguments(self, parser):
        parser.add_argument('securedrops', nargs='*', type=str, default='',
            help=("Specify one or more domain names of securedrop landing pages "
                  " to scan. Specify the domain name with the 'https://' or "
                  "'http://' removed. If unspecified, scan all landing pages in the "
                  "directory."))

    def handle(self, *args, **options):
        if options['securedrops']:
            securedrops = []
            for domain_name in options['securedrops']:
                try:
                    # Handle full URL
                    securedrop = Securedrop.objects.get(
                        landing_page_domain=domain_name
                    )
                    securedrops.append(securedrop)
                except Securedrop.DoesNotExist:
                    # Also handle if it's just the domain
                    try:
                        securedrop = Securedrop.objects.get(
                            landing_page_domain='https://{}'.format(domain_name)
                        )
                        securedrops.append(securedrop)
                    except Securedrop.DoesNotExist:
                        msg = "Landing page '{}' does not exist".format(
                            'https://{}'.format(domain)
                        )
                        raise CommandError(msg)
        else:
            securedrops = Securedrop.objects.all()

        bulk_scan(securedrops)
        self.stdout.write('Scanning complete! Results added to database.')
