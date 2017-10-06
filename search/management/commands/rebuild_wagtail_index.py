from django.core.management.base import BaseCommand
from django.db import transaction

from wagtail.wagtailcore.models import Page

from search.models import SearchDocument


class Command(BaseCommand):
    help = 'Rebuild the SearchDocument instances for Wagtail pages'

    @transaction.atomic
    def handle(self, *args, **options):
        SearchDocument.objects.filter(result_type='W').delete()
        live_pages = Page.objects.live().specific()
        bulk_create_data = []

        for page in live_pages:

            if page.is_root():
                continue  # Don't index root pages

            search_content = page.get_search_content() if hasattr(page, 'get_search_content') else ''
            document = SearchDocument(
                title=page.title,
                url=page.full_url,
                search_content=search_content,
                data={},
                result_type='W',
                key='wagtail-page-{}'.format(page.pk)
            )
            bulk_create_data.append(document)

        SearchDocument.objects.bulk_create(bulk_create_data)
