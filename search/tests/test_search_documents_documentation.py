import os

import vcr
from django.test import TestCase

from search.models import SearchDocument
from search.utils.documentation import (
    READTHEDOCS_BASE,
    fetch_indexable_pages,
    index_documentation_pages,
)


VCR_DIR = os.path.join(os.path.dirname(__file__), 'search_vcr')


class FetchPagesTestCase(TestCase):
    @vcr.use_cassette(os.path.join(VCR_DIR, 'fetch-root.yaml'))
    def test_fetching_sites_returns_list_of_urls(self):
        urls = fetch_indexable_pages()
        self.assertTrue(len(urls) > 0)
        for url in urls:
            self.assertTrue(url.startswith(READTHEDOCS_BASE))


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
            self.assertNotEqual(doc.search_content, '')
