from django.test import TestCase

from landing_page_checker.tests.factories import SecuredropPageFactory


class TestSecuredropPage(TestCase):
    def setUp(self):
        self.title = 'Awesome'
        self.landing_page_domain = 'https://landing.com'
        self.onion_address = 'something.onion'
        self.description = 'Amaze'
        self.sd = SecuredropPageFactory(
            title=self.title,
            landing_page_domain=self.landing_page_domain,
            onion_address=self.onion_address,
            organization_description=self.description
        )
        self.search_content = self.sd.get_search_content()

    def test_get_search_content_indexes_title(self):
        self.assertIn(self.title, self.search_content)

    def test_get_search_content_indexes_landing_page_domain(self):
        self.assertIn(self.landing_page_domain, self.search_content)

    def test_get_search_content_indexes_onion_address(self):
        self.assertIn(self.onion_address, self.search_content)

    def test_get_search_content_indexes_description(self):
        self.assertIn(self.onion_address, self.search_content)

    def test_get_search_content_indexes_languages(self):
        language = self.sd.languages.first().title
        self.assertIn(language, self.search_content)

    def test_get_search_content_indexes_topics(self):
        topic = self.sd.topics.first().title
        self.assertIn(topic, self.search_content)

    def test_get_search_content_indexes_countries(self):
        country = self.sd.countries.first().title
        self.assertIn(country, self.search_content)
