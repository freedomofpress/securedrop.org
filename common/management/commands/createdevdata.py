from common.models import SocialSharingSEOSettings, CustomImage
from home.models import HomePage
from home.tests.factories import HomePageFactory

from wagtail.wagtailcore.models import Page, Site

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core import management


class Command(BaseCommand):
    help = 'Creates data appropriate for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete homepage and child pages before creating new data.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['delete']:
            Page.objects.filter(slug='home').delete()

        try:
            HomePage.objects.get(slug='home')
        except ObjectDoesNotExist:
            Page.objects.filter(slug='home').delete()
            # homepage cannot be saved without a parent
            home_page = HomePageFactory.build(
                description_header="Share and accept documents securely."
            )

            root_page = Page.objects.get(title='Root')
            root_page.add_child(instance=home_page)

            site = Site.objects.create(
                site_name='SecureDrop.org (Dev)',
                hostname='localhost',
                port='8000',
                root_page=home_page,
                is_default_site=True
            )

            image = CustomImage.objects.filter(title='Sample Image').first()
            if not image:
                image = CustomImage.objects.create(
                    title='Sample Image',
                    file=ImageFile(open('common/static/images/securedrop.png', 'rb'), name='logo.png'),
                    attribution='createdevdata'
                )

            sssettings = SocialSharingSEOSettings.for_site(site)
            sssettings.default_description = 'SecureDrop'
            sssettings.default_image = image
            sssettings.save()

            home_page.save()
            site.save()

        management.call_command('createblogdata', '10')
        management.call_command('createdirectory', '10')
        management.call_command('createnavmenu')
        management.call_command('createfootersettings')
        management.call_command('createresultgroups')

        # Create superuser
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                'test',
                'test@securedrop',
                'test',
            )
            self.stdout.write(
                'Superuser created:\n'
                '\tname: test\n'
                '\temail: test@securedrop\n'
                '\tpassword: test'
            )
