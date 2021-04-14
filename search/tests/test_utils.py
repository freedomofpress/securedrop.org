from django.test import TestCase

from search.models import SearchDocument
from search.tests.factories import SearchDocumentFactory
from search.utils.management import flush_documents_by_type


class FlushTestCase(TestCase):
    def setUp(self):
        SearchDocumentFactory(result_type='W')
        SearchDocumentFactory(result_type='D')

    def test_flush_should_remove_all_documents_by_type(self):
        flush_documents_by_type('W')
        self.assertEqual(SearchDocument.objects.filter(result_type='W').count(), 0)
        self.assertEqual(SearchDocument.objects.filter(result_type='D').count(), 1)
