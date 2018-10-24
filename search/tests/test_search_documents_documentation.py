from unittest import mock
import os

import vcr
from django.test import TestCase

from search.models import SearchDocument
from search.tests.factories import SearchDocumentFactory
from search.utils.documentation import (
    READTHEDOCS_BASE,
    fetch_indexable_pages,
    index_documentation_pages,
    index_documentation_page,
)


VCR_DIR = os.path.join(os.path.dirname(__file__), 'search_vcr')


class FetchPagesTestCase(TestCase):
    @vcr.use_cassette(os.path.join(VCR_DIR, 'fetch-root.yaml'))
    def test_fetching_sites_returns_list_of_urls(self):
        urls = fetch_indexable_pages()
        self.assertTrue(len(urls) > 0)
        for url in urls:
            self.assertTrue(url.startswith(READTHEDOCS_BASE))


class IndexPagesTestCase(TestCase):
    def test_should_use_a_default_title_if_none_exists(self):
        url = 'https://example.com'
        page = mock.Mock(content='<div role="main">new content</div>')
        index_documentation_page(url, page)
        self.assertEqual(
            SearchDocument.objects.get(key=url).title,
            url,
        )

    def test_should_update_pages_if_they_already_exist(self):
        url = 'https://example.com'
        page = mock.Mock(content='<div role="main">frabjous content</div>')
        SearchDocumentFactory(
            url=url,
            search_content='old content',
            key=url,
        )
        index_documentation_page(url, page)

        self.assertEqual(
            SearchDocument.objects.get(key=url).search_content,
            'frabjous content',
        )

        self.assertEqual(
            SearchDocument.objects.filter(search_vector='frabjous').count(),
            1,
        )


class UpdateDocumentationIndexTestCase(TestCase):
    @vcr.use_cassette(os.path.join(VCR_DIR, 'fetch-all.yaml'))
    def test_update_documentation_search_documents(self):
        index_documentation_pages()
        for url in fetch_indexable_pages():
            self.assertTrue(
                SearchDocument.objects.filter(url=url).exists(),
                'Search document with url %r should have been created' % url,
            )
            doc = SearchDocument.objects.get(url=url)
            self.assertNotEqual(doc.title, '')
            self.assertEqual(doc.result_type, 'D')
            self.assertEqual(doc.key, url)
            self.assertNotEqual(doc.search_vector, '')
