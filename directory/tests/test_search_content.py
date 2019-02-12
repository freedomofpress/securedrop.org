from django.test import TestCase

from directory.tests.factories import DirectoryPageFactory
from wagtail.core.rich_text import RichText


class TestDirectoryPage(TestCase):
    def setUp(self):
        self.title = 'Awesome'
        self.body = 'Cool'
        self.source_warning = 'Alert'
        self.directory = DirectoryPageFactory(
            title=self.title,
            body=RichText(self.body),
            source_warning=self.source_warning
        )
        self.search_content = self.directory.get_search_content()

    def test_get_search_content_indexes_title(self):
        self.assertIn(self.title, self.search_content.text)

    def test_get_search_content_indexes_body(self):
        self.assertIn(self.body, self.search_content.text)

    def test_get_search_content_indexes_source_warning(self):
        self.assertIn(self.source_warning, self.search_content.text)
