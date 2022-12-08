from django.test import TestCase
from wagtail.rich_text import RichText

from home.tests.factories import HomePageFactory


class TestHomepage(TestCase):
    def setUp(self):
        self.title = 'Awesome'
        self.description = 'Cool'
        self.features_header = 'Features'
        self.instances_header = 'Instances'
        self.home = HomePageFactory(
            title=self.title,
            description=RichText(self.description),
            features_header=self.features_header,
            instances_header=self.instances_header,
        )
        self.search_content = self.home.get_search_content()

    def test_get_search_content_indexes_title(self):
        self.assertIn(self.title, self.search_content.text)

    def test_get_search_content_indexes_description(self):
        self.assertIn(self.description, self.search_content.text)

    def test_get_search_content_indexes_features_header(self):
        self.assertIn(self.features_header, self.search_content.text)

    def test_get_search_content_indexes_instances_header(self):
        self.assertIn(self.instances_header, self.search_content.text)
