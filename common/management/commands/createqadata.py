from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from wagtail.models import Page, Site

from directory.models import Country, DirectoryEntry, DirectoryPage, Language, Topic
from directory.tests.factories import ScanResultFactory
from home.models import HomePage
from home.tests.factories import HomePageFactory


class Command(BaseCommand):
    help = (
        "Populate the database with the small, deterministic site that our "
        "Playwright QA test suite in e2e/ expects. This will tear down "
        "existing content before recreating it."
    )

    def get_home_page(self):
        return HomePage.objects.get(slug="home")

    def generate_home_page(self):
        self.stdout.write("Building home page")

        # Clear any prior default site & home page (Wagtail's welcome page on a
        # fresh DB, or our own home on a re-run) so this is idempotent.
        # Delete the site first to free the root_page FK.
        Site.objects.filter(is_default_site=True).delete()
        Page.objects.filter(slug="home").delete()

        root = Page.objects.filter(depth=1).first()
        if root is None:
            root = Page.add_root(instance=Page(title="Root"))

        home = HomePageFactory(
            parent=root,
            title="SecureDrop",
            slug="home",
            description_header="Share and accept documents securely.",
            description=(
                "<p>SecureDrop is an open-source whistleblower submission "
                "system for securely accepting documents from anonymous "
                "sources.</p>"
            ),
        )

        Site.objects.create(
            root_page=home,
            hostname="localhost",
            port=8000,
            is_default_site=True,
            site_name="SecureDrop.org (QA)",
        )
        return home

    def get_taxonomy(self, model, *titles):
        return [model.objects.get_or_create(title=title)[0] for title in titles]

    def generate_directory(self):
        self.stdout.write("Building directory")
        home_page = self.get_home_page()
        directory = home_page.add_child(
            instance=DirectoryPage(title="Directory", slug="directory")
        )

        directory.add_child(
            instance=DirectoryEntry(
                title="Alpha Gazette",
                slug="alpha-gazette",
                landing_page_url="https://alpha-gazette.example/securedrop",
                onion_address="http://alpha-gazette.example.onion",
                languages=self.get_taxonomy(Language, "English"),
                countries=self.get_taxonomy(Country, "United States"),
                topics=self.get_taxonomy(Topic, "Corruption"),
            )
        )
        ScanResultFactory(
            landing_page_url="https://alpha-gazette.example/securedrop",
            no_failures=True,
        )

        directory.add_child(
            instance=DirectoryEntry(
                title="Beta Chronicle",
                slug="beta-chronicle",
                landing_page_url="https://beta-chronicle.example/securedrop",
                onion_address="http://beta-chronicle.example.onion",
                languages=self.get_taxonomy(Language, "Portugese"),
                countries=self.get_taxonomy(Country, "Brazil"),
                topics=self.get_taxonomy(Topic, "Environment"),
            )
        )
        directory.add_child(
            instance=DirectoryEntry(
                title="Gamma Observer",
                slug="gamma-observer",
                landing_page_url="https://gamma-observer.example/securedrop",
                onion_address="http://gamma-observer.example.onion",
                languages=self.get_taxonomy(Language, "English", "German"),
                countries=self.get_taxonomy(Country, "Germany"),
                topics=self.get_taxonomy(Topic, "Corruption", "Public health"),
            )
        )
        # A non-ASCII slug
        directory.add_child(
            instance=DirectoryEntry(
                title="Zeitung Überblick",
                slug="zeitung-überblick",
                landing_page_url="https://zeitung-uberblick.example/securedrop",
                onion_address="http://zeitung-uberblick.example.onion",
                languages=self.get_taxonomy(Language, "German"),
                countries=self.get_taxonomy(Country, "Germany"),
                topics=self.get_taxonomy(Topic, "Environment"),
            )
        )

        return directory

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Creating QA data... ", "")
        self.stdout.flush()

        call_command("loaddata", "devuser", verbosity=0)

        # Generate the page tree
        self.generate_home_page()
        self.generate_directory()

        self.stdout.write(self.style.SUCCESS("Done"))
