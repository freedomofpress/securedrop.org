from blog.models import BlogIndexPage
from blog.tests.factories import BlogIndexPageFactory
from directory.models import DirectoryPage
from directory.tests.factories import DirectoryPageFactory
from home.models import HomePage
from marketing.models import MarketingIndexPage
from marketing.tests.factories import MarketingPageFactory
from menus.models import Menu, MenuItem

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Creates the main nav menu'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete nav menu before creating new data.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['delete']:
            Menu.objects.filter(slug='main').delete()

        if not Menu.objects.filter(slug='main').exists():
            main = Menu.objects.create(name='Main Menu', slug='main')

            home_page = HomePage.objects.get(slug='home')

            if BlogIndexPage.objects.first():
                blog_index_page = BlogIndexPage.objects.first()
            else:
                blog_index_page = BlogIndexPageFactory(parent=home_page, title="News")

            if DirectoryPage.objects.first():
                directory = DirectoryPage.objects.first()
            else:
                directory = DirectoryPageFactory(parent=home_page, title="Directory")

            if MarketingIndexPage.objects.first():
                marketing = MarketingIndexPage.objects.first()
            else:
                marketing = MarketingPageFactory(parent=home_page, title="Features")

            MenuItem.objects.bulk_create([
                MenuItem(
                    text='Overview',
                    link_page=marketing,
                    menu=main,
                    sort_order=1
                ),
                MenuItem(
                    text='News',
                    link_page=blog_index_page,
                    menu=main,
                    sort_order=2
                ),
                MenuItem(
                    text='Instance Directory',
                    link_page=directory,
                    menu=main,
                    sort_order=3
                ),
                MenuItem(
                    text='Contribute',
                    link_url='#',
                    menu=main,
                    sort_order=4,
                ),
                MenuItem(
                    text='Support',
                    link_url='#',
                    menu=main,
                    sort_order=5,
                ),
            ])
