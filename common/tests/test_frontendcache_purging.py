from unittest.mock import patch

from django.test import TestCase
from wagtail.core.models import Site
from wagtail_factories import PageFactory

from common.models.settings import FooterSettings


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

    def test_cache_purge__edit_page(self, purge_mock):
        "Changing a page should purge the entire zone"
        page = PageFactory.create(parent=None)
        purge_mock.reset()

        page.text = 'New Text'
        page.save()
        purge_mock.assert_called_once()

    def test_cache_purge__edit_footer_settings(self, purge_mock):
        """
        Changing any Setting should purge the entire zone. In this
        case we test with FooterSettings as an example, but it should work for
        any BaseSetting subclass
        """

        site = Site.objects.get(is_default_site=True)
        footer_settings = FooterSettings.for_site(site)
        footer_settings.securedrop_onion_address = 'notanonion.onion'
        footer_settings.save()
        purge_mock.assert_called_once()
