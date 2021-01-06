from django.test import TestCase
from django.urls import reverse
from wagtail.core.models import Site

from directory.tests.factories import (
    DirectoryPageFactory,
    DirectoryEntryFactory,
    ScanResultFactory,
)


class ApiTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.directory = DirectoryPageFactory(
            parent=Site.objects.get().root_page,
        )
        cls.entry = DirectoryEntryFactory(parent=cls.directory)

    def test_directory_is_at_api_root(self):
        response = self.client.get(reverse('api-root'), format='json')

        self.assertIn('directory', response.data)

    def test_directory_entry_data_is_correct(self):
        response = self.client.get(reverse('directoryentry-list'), format='json')

        self.assertEqual(dict(response.data[0]), {
            'title': self.entry.title,
            'slug': self.entry.slug,
            'directory_url': self.entry.full_url,
            'first_published_at': self.entry.first_published_at,
            'landing_page_url': self.entry.landing_page_url,
            'onion_address': self.entry.onion_address,
            'onion_name': self.entry.onion_name,
            'organization_logo': self.entry.organization_logo,
            'organization_description': self.entry.organization_description,
            'organization_url': self.entry.organization_url,
            'countries': [country.title for country in self.entry.countries.all()],
            'topics': [topic.title for topic in self.entry.topics.all()],
            'languages': [lang.title for lang in self.entry.languages.all()],
            'latest_scan': None,
        })


class ApiLatestScanResultTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.directory = DirectoryPageFactory(
            parent=Site.objects.get().root_page,
        )
        cls.entry = DirectoryEntryFactory(parent=cls.directory)

        cls.scan_fail = ScanResultFactory(
            landing_page_url=cls.entry.landing_page_url,
            severe_warning=True,
            securedrop=cls.entry,
        )
        cls.scan_pass = ScanResultFactory(
            landing_page_url=cls.entry.landing_page_url,
            no_failures=True,
            securedrop=cls.entry,
        )

    def test_scan_result_data_is_correct(self):
        response = self.client.get(reverse('directoryentry-list'), format='json')
        # The diffs for the dict in this test can be quite large
        self.maxDiff = 1500
        self.assertEqual(dict(response.data[0]['latest_scan']), {
            'live': True,
            'landing_page_url': self.entry.landing_page_url,
            'result_last_seen': self.scan_pass.result_last_seen.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'forces_https': True,
            'hsts': True,
            'hsts_max_age': True,
            'hsts_entire_domain': True,
            'hsts_preloaded': True,
            'http_status_200_ok': True,
            'no_cross_domain_redirects': True,
            'no_cross_domain_assets': True,
            'expected_encoding': True,
            'no_server_info': True,
            'no_server_version': True,
            'csp_origin_only': True,
            'mime_sniffing_blocked': True,
            'noopen_download': True,
            'xss_protection': True,
            'clickjacking_protection': True,
            'good_cross_domain_policy': True,
            'http_1_0_caching_disabled': True,
            'cache_control_set': True,
            'cache_control_revalidate_set': True,
            'cache_control_nocache_set': True,
            'cache_control_notransform_set': True,
            'cache_control_nostore_set': True,
            'cache_control_private_set': True,
            'expires_set': True,
            'referrer_policy_set_to_no_referrer': True,
            'safe_onion_address': True,
            'no_cdn': True,
            'no_analytics': True,
            'subdomain': False,
            'no_cookies': True,
            'http2': True,
            'redirect_target': None,
            'grade': 'A',
        })
