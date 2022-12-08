import requests
import time

from wagtail.models import Page, Site
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core import management
import factory
import wagtail_factories

from common.models import SocialSharingSEOSettings, CustomImage
from common.factories import CustomImageFactory
from home.models import HomePage
from home.tests.factories import HomePageFactory


class Command(BaseCommand):
    help = 'Creates data appropriate for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-download',
            action='store_false',
            dest='download_images',
            help='Download external images',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete homepage and child pages before creating new data.',
        )

    def fetch_image(self, width, height, collection, category):
        url = 'https://placeimg.com/{width}/{height}/{category}'.format(
            width=width, height=height, category=category
        )
        response = requests.get(url)
        if response and response.content:
            CustomImageFactory(
                file__from_file=ContentFile(response.content),
                file_size=len(response.content),
                width=width,
                height=height,
                collection=collection,
            )
        else:
            return False
        time.sleep(0.2)
        return True

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
                description_header="Share and accept documents securely.",
                slug="home"
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
                    file=ImageFile(open('common/static/images/logo_solid_white.png', 'rb'), name='logo'),
                    attribution='createdevdata'
                )
            sssettings = SocialSharingSEOSettings.for_site(site)
            sssettings.default_description = 'SecureDrop'
            sssettings.default_image = image
            sssettings.save()

            home_page.save()
            site.save()

        # IMAGES
        icon_collection = wagtail_factories.CollectionFactory(name='Icons')

        if options.get('download_images', True):
            self.stdout.write('Fetching images')
            self.stdout.flush()
            image_fail = False
            for i in range(15):
                if not self.fetch_image(500, 500, icon_collection, 'animals'):
                    image_fail = True
            if image_fail:
                self.stdout.write(self.style.NOTICE('NOTICE: Some images failed to save'))
            else:
                self.stdout.write(self.style.SUCCESS('OK'))
        else:
            faker = factory.faker.Faker._get_faker(locale='en-US')
            for i in range(20):
                CustomImageFactory.create(
                    file__width=500,
                    file__height=500,
                    file__color=faker.safe_color_name(),
                    collection=icon_collection,
                )

        management.call_command('createblogdata', '10')
        management.call_command('createdirectory', '10')
        management.call_command('createnavmenu')
        management.call_command('createfootersettings')
        management.call_command('createresultgroups')
        management.call_command('createsearchmenus')
        management.call_command('createmarketing')

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
