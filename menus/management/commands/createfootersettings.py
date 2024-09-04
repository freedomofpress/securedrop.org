from blog.models import BlogIndexPage
from blog.tests.factories import BlogIndexPageFactory
from common.models import FooterSettings
from home.models import HomePage
from menus.models import Menu, MenuItem
from simple.models import SimplePage

from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from wagtail.models import Page, Site
from wagtail.rich_text import RichText


class Command(BaseCommand):
    help = 'Creates the footer and footer menus'

    @transaction.atomic
    def handle(self, *args, **options):
        site = Site.objects.get(site_name='SecureDrop.org (Dev)')
        home_page = HomePage.objects.get(slug='home')
        donation_url = 'https://freedom.press/crowdfunding/securedrop/'

        footer_settings = FooterSettings.for_site(site)
        footer_settings.title = RichText('SecureDrop is a project of <a href="https://freedom.press">Freedom of the Press Foundation</a>.')
        footer_settings.release_key = 'abcdefghijklmonopqrs'

        try:
            contribute_page = Page.objects.get(slug='contribute')
        except ObjectDoesNotExist:
            contribute_page = SimplePage(title='Contribute', slug='contribute')
            home_page.add_child(instance=contribute_page)

        footer_settings.donation_link = donation_url
        footer_settings.contribute_link = contribute_page

        footer_menu, fm_created = Menu.objects.get_or_create(
            name='Footer Menu', slug='footer_menu')
        if fm_created:
            if BlogIndexPage.objects.first():
                blog_index_page = BlogIndexPage.objects.first()
            else:
                blog_index_page = BlogIndexPageFactory(parent=home_page)

            MenuItem.objects.bulk_create([
                MenuItem(
                    text='Donate',
                    link_url=donation_url,
                    menu=footer_menu,
                    sort_order=1
                ),
                MenuItem(
                    text='Contribute Code',
                    link_page=contribute_page,
                    menu=footer_menu,
                    sort_order=2
                ),
                MenuItem(
                    text='Get Support',
                    link_url='#',
                    menu=footer_menu,
                    sort_order=3
                ),
                MenuItem(
                    text='Media',
                    link_url='#',
                    menu=footer_menu,
                    sort_order=4,
                ),
                MenuItem(
                    text='Privacy Policy',
                    link_url='#',
                    menu=footer_menu,
                    sort_order=5,
                ),
                MenuItem(
                    text='News',
                    link_page=blog_index_page,
                    menu=footer_menu,
                    sort_order=5,
                ),
            ])

        footer_settings.main_menu = footer_menu

        support_menu, sm_created = Menu.objects.get_or_create(
            name='Support Menu', slug='support_menu')
        if sm_created:
            MenuItem.objects.bulk_create([
                MenuItem(
                    text='Documentation',
                    link_url='#',
                    menu=support_menu,
                    sort_order=1
                ),
                MenuItem(
                    text='Guide for Journalists',
                    link_url='#',
                    menu=support_menu,
                    sort_order=3
                ),
                MenuItem(
                    text='Guide for Administrators',
                    link_url='#',
                    menu=support_menu,
                    sort_order=4,
                ),
            ])

        footer_settings.support_menu = support_menu

        footer_settings.save()
