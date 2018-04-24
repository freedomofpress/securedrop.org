from unittest.mock import patch

from django.test import TestCase
from wagtail_factories import PageFactory


@patch('common.signals.purge_all_from_cache')
class FrontendCacheTestCase(TestCase):
    def test_cache_purge__new_page(self, purge_mock):
        "Creating a new page should purge the entire zone"
        PageFactory.create(parent=None)
        purge_mock.assert_called_once()

    def test_cache_purge__delete_page(self, purge_mock):
        "Deleting a page should purge the entire zone"
        page = PageFactory.create(parent=None)
        purge_mock.reset()

        page.delete()
        purge_mock.assert_called_once()

    def test_update_menu_item_purges_cache(self, purge_mock):
        "Changing a page should purge the entire zone"
        page = PageFactory.create(parent=None)
        purge_mock.reset()

        page.text = 'New Text'
        page.save()
        purge_mock.assert_called_once()
