from home.models import HomePage

from wagtail.wagtailcore.models import Page, Site

from django.core.management.base import BaseCommand
from django.db import transaction
from django.core import management


class Command(BaseCommand):
    help = 'Creates data appropriate for development'

    @transaction.atomic
    def handle(self, *args, **options):
        Page.objects.get(slug='home').delete()
        home_page = HomePage(title='Home', slug='home')
        root_page = Page.objects.get(title='Root')
        root_page.add_child(instance=home_page)

        Site.objects.create(
            site_name='SecureDrop.org (Dev)',
            hostname='localhost',
            port='8000',
            root_page=home_page,
            is_default_site=True
        )

        management.call_command('createblogdata', '10')
