from django.urls import reverse
from django.db.models import Func, Value
from django.test import TestCase

from search.tests.factories import SearchDocumentFactory


class SearchTestCase(TestCase):
    def test_search(self):
        sd1 = SearchDocumentFactory(
            search_vector=Func(Value('Tony Stark'), function='to_tsvector')
        )

        sd2 = SearchDocumentFactory(
            search_vector=Func(Value('Howard Stark'), function='to_tsvector')
        )

        sd3 = SearchDocumentFactory(
            search_vector=Func(Value('Pepper Potts'), function='to_tsvector')
        )
        search_response = self.client.get('/search/?query=stark')
        results = search_response.context['search_results'].paginator.object_list
        # Assert that search results contain both starks, but not pepper
        self.assertTrue(results.filter(id=sd1.pk).exists())
        self.assertTrue(results.filter(id=sd2.pk).exists())
        self.assertFalse(results.filter(id=sd3.pk).exists())

    def test_search_handles_null_characters(self):
        query_with_nulls = '\x00'
        response = self.client.get(
            reverse('search'), {'query': query_with_nulls}
        )
        self.assertEqual(response.status_code, 200)
