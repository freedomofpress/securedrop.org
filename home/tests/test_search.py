import json
from django.test import TestCase

from home.tests.factories import HomePageFactory


class TestHomepage(TestCase):
    def setUp(self):
        self.title = 'Awesome'
        self.description = 'Cool'
        self.features_title = 'Features'
        self.instances_title = 'Instances'
        self.home = HomePageFactory(
            title=self.title,
            description=json.dumps([
                {'type': 'rich_text', 'value': self.description}
            ]),
            features_title=self.features_title,
            instances_title=self.instances_title,
        )
        self.search_content = self.home.get_search_content()

    def test_get_search_content_indexes_title(self):
        self.assertIn(self.title, self.search_content)

    def test_get_search_content_indexes_description(self):
        self.assertIn(self.description, self.search_content)

    def test_get_search_content_index_blog_page_titles(self):
        self.assertIn(self.blog_title, self.search_content)

    def test_get_search_content_indexes_features_title(self):
        self.assertIn(self.features_title, self.search_content)

    def test_get_search_content_indexes_instances_title(self):
        self.assertIn(self.instances_title, self.search_content)
