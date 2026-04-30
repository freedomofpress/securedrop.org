import os

from wagtail.models import Page, Site
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.management import call_command
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core import management

from common.models import SocialSharingSEOSettings, CustomImage
from home.models import HomePage
from home.tests.factories import HomePageFactory


class Command(BaseCommand):
    help = "Creates data appropriate for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            dest="delete",
            default=False,
            help="Delete homepage and child pages before creating new data.",
        )

    def _copy_files(self, local_storage, path):
        """
        Recursively copy files from local_storage to default_storage.
        """
        directories, file_names = local_storage.listdir(path)
        for directory in directories:
            self._copy_files(local_storage, path + directory + "/")
        for file_name in file_names:
            with local_storage.open(path + file_name) as file_:
                default_storage.save(path + file_name, file_)

    @transaction.atomic
    def handle(self, *args, **options):
        if options["delete"]:
            Page.objects.filter(slug="home").delete()

        try:
            HomePage.objects.get(slug="home")
        except ObjectDoesNotExist:
            Page.objects.filter(slug="home").delete()
            # homepage cannot be saved without a parent
            home_page = HomePageFactory.build(
                description_header="Share and accept documents securely.", slug="home"
            )

            root_page = Page.objects.get(title="Root")
            root_page.add_child(instance=home_page)

            site = Site.objects.create(
                site_name="SecureDrop.org (Dev)",
                hostname="localhost",
                port="8000",
                root_page=home_page,
                is_default_site=True,
            )
            image = CustomImage.objects.filter(title="Sample Image").first()
            if not image:
                image = CustomImage.objects.create(
                    title="Sample Image",
                    file=ImageFile(
                        open("common/static/images/logo_solid_white.png", "rb"),
                        name="logo",
                    ),
                    attribution="createdevdata",
                )
            sssettings = SocialSharingSEOSettings.for_site(site)
            sssettings.default_description = "SecureDrop"
            sssettings.default_image = image
            sssettings.save()

            home_page.save()
            site.save()

        # IMAGES
        fixtures_dir = os.path.join("common", "fixtures")
        fixture_file = os.path.join(fixtures_dir, "devdata.json")
        self.stdout.write("Copying media files...")
        local_storage = FileSystemStorage(os.path.join(fixtures_dir, "media"))
        self._copy_files(local_storage, "")
        call_command("loaddata", fixture_file, verbosity=4)

        management.call_command("createblogdata", "10")
        management.call_command("createdirectory", "10")
        management.call_command("createnavmenu")
        management.call_command("createfootersettings")
        management.call_command("createresultgroups")
        management.call_command("createsearchmenus")
        management.call_command("createmarketing")

        # Create superuser
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                "test",
                "test@securedrop",
                "test",
            )
            self.stdout.write(
                "Superuser created:\n"
                "\tname: test\n"
                "\temail: test@securedrop\n"
                "\tpassword: test"
            )
