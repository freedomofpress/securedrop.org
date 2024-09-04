from home.models import HomePage
from menus.models import Menu, MenuItem
from simple.models import SimplePage

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Creates the two search menus and creates guide pages if menus and pages do not exist.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete existing search menus before creating new ones',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['delete']:
            Menu.objects.filter(slug='search-docs').delete()
            Menu.objects.filter(slug='search-guides').delete()

        if not Menu.objects.filter(slug='search-docs').exists():
            docs = Menu.objects.create(name='Search Docs', slug='search-docs')

            MenuItem.objects.bulk_create([
                MenuItem(
                    text='Documentation',
                    link_url='https://docs.securedrop.org/en/stable/',
                    menu=docs,
                    sort_order=1
                ),
            ])

        if not Menu.objects.filter(slug='search-guides').exists():
            guides = Menu.objects.create(name='Search Guides', slug='search-guides')
            home_page = HomePage.objects.get(slug='home')
            j = SimplePage(title='Guide for Journalists')
            a = SimplePage(title='Guide for Administrators')
            s = SimplePage(title='Guide for Sources')
            home_page.add_child(instance=j)
            home_page.add_child(instance=a)
            home_page.add_child(instance=s)

            MenuItem.objects.bulk_create([
                MenuItem(
                    text='For Journalists',
                    link_page=j,
                    menu=guides,
                    sort_order=1
                ),
                MenuItem(
                    text='For Administrators',
                    link_page=a,
                    menu=guides,
                    sort_order=2
                ),
                MenuItem(
                    text='For Sources',
                    link_page=s,
                    menu=guides,
                    sort_order=3
                ),
            ])
