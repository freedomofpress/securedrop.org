import random


from blog.models import BlogIndexPage, CategoryPage
from blog.tests.factories import BlogPageFactory, BlogIndexPageFactory, CategoryPageFactory
from home.models import HomePage

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Creates blog data appropriate for development'

    def add_arguments(self, parser):
        parser.add_argument('number_of_posts', type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        number_of_posts = options['number_of_posts']

        home_page = HomePage.objects.get(slug='home')

        if BlogIndexPage.objects.all():
            blog_index_page = BlogIndexPage.objects.all().first()
        else:
            blog_index_page = BlogIndexPageFactory(parent=home_page)

        CATEGORY_NAMES = [
            'Release Announcement',
            'Pre-Release Announcement',
            'Interest Article',
            'Security Advisory',
        ]

        categories = []
        for name in CATEGORY_NAMES:
            try:
                category_page = CategoryPage.objects.get(title=name)
            except ObjectDoesNotExist:
                category_page = CategoryPageFactory(title=name, parent=home_page)

            categories.append(category_page)

        for x in range(number_of_posts):
            blog_page = BlogPageFactory(parent=blog_index_page)
            blog_page.categories = [random.choice(categories)]
            blog_page.save()
