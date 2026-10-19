from django.core.management.base import BaseCommand
from django.db import transaction

from wagtail.models import Page, Site

from home.tests.factories import HomePageFactory


class Command(BaseCommand):
    help = (
        "Populate the database with the small, deterministic site that our "
        "Playwright QA test suite in e2e/ expects. This will tear down "
        "existing content before recreating it."
    )

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

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Creating QA data... ", "")
        self.stdout.flush()

        # Generate the page tree
        self.generate_home_page()

        self.stdout.write(self.style.SUCCESS("Done"))
