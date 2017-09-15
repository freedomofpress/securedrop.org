from blog.models import BlogIndexPage
from blog.tests.factories import BlogIndexPageFactory
from home.models import HomePage
from menus.models import Menu, MenuItem

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Creates the main nav menu'

    @transaction.atomic
    def handle(self, *args, **options):
        if not Menu.objects.filter(slug='main').exists():
            main = Menu.objects.create(name='Main Menu', slug='main')

            home_page = HomePage.objects.get(slug='home')

            if BlogIndexPage.objects.first:
                blog_index_page = BlogIndexPage.objects.first()
            else:
                blog_index_page = BlogIndexPageFactory(parent=home_page)

            MenuItem.objects.bulk_create([
                MenuItem(
                    text='Overview',
                    link_url='#',
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
                    link_url='#',
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
