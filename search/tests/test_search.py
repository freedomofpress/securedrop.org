from django.test import TestCase

from search.tests.factories import SearchDocumentFactory


class SearchTestCase(TestCase):
    def test_search(self):
        sd1 = SearchDocumentFactory(title='Tony Stark', search_content='')
        sd2 = SearchDocumentFactory(title='Howard Stark', search_content='')
        sd3 = SearchDocumentFactory(title='Pepper Potts', search_content='')
        search_response = self.client.get('/search/?query=stark')
        results = search_response.context['search_results'].paginator.object_list
        # Assert that search results contain both starks, but not pepper
        self.assertTrue(results.filter(id=sd1.pk).exists())
        self.assertTrue(results.filter(id=sd2.pk).exists())
        self.assertFalse(results.filter(id=sd3.pk).exists())
