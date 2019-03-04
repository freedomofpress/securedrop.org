from unittest.mock import patch

from django.test import TestCase
from wagtail.core.models import Site
from wagtail_factories import PageFactory

from common.models.settings import FooterSettings


class FrontendCacheTestCase(TestCase):
    @patch('common.signals.purge_all_from_cache')
    def test_cache_purge__publish_page(self, purge_mock):
        "Creating a new page should purge the entire zone"
        page = PageFactory.create(parent=None)
        revision = page.save_revision()
        revision.publish()

        self.assertEqual(purge_mock.call_count, 1)

    def test_cache_purge__delete_page(self):
        "Deleting a page should purge the entire zone"
        page = PageFactory.create(parent=None)

        with patch('common.signals.purge_all_from_cache') as purge_mock:
            page.delete()
            self.assertEqual(purge_mock.call_count, 1)

    def test_cache_purge__delete_footer_settings(self):
        "Changing a page should purge the entire zone"

        site = Site.objects.get(is_default_site=True)
        footer_settings = FooterSettings.for_site(site)
        with patch('common.signals.purge_all_from_cache') as purge_mock:
            footer_settings.delete()
            self.assertEqual(purge_mock.call_count, 1)

    def test_cache_purge__edit_footer_settings(self):
        """
        Changing any Setting should purge the entire zone. In this
        case we test with FooterSettings as an example, but it should work for
        any BaseSetting subclass
        """

        site = Site.objects.get(is_default_site=True)
        footer_settings = FooterSettings.for_site(site)
        footer_settings.securedrop_onion_address = 'notanonion.onion'
        with patch('common.signals.purge_all_from_cache') as purge_mock:
            footer_settings.save()
            self.assertEqual(purge_mock.call_count, 1)
