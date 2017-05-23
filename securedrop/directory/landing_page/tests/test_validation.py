from bs4 import BeautifulSoup
import os
from unittest import mock

from django.test import TestCase
import vcr

from directory.landing_page import validation
from directory.models import Securedrop, Result


VCR_DIR = os.path.join(os.path.dirname(__file__), 'scans_vcr')


class VerificationUtilityTest(TestCase):
    def test_onion_link_is_in_href(self):
        test_html = "<a href='notavalidaddress.onion'>SecureDrop</a>"
        soup = BeautifulSoup(test_html, "lxml")
        self.assertFalse(validation.validate_onion_address_not_in_href(soup))

    def test_onion_link_is_not_in_href(self):
        test_html = "Go to notavalidaddress.onion and leak dem docs"
        soup = BeautifulSoup(test_html, "lxml")
        self.assertTrue(validation.validate_onion_address_not_in_href(soup))

    def test_url_does_not_have_subdomain(self):
        self.assertFalse(validation.validate_subdomain('https://example.com/securedrop'))

    def test_url_does_have_subdomain(self):
        self.assertTrue(validation.validate_subdomain('https://securedrop.example.com'))

    def test_www_url_does_not_have_subdomain(self):
        self.assertFalse(validation.validate_subdomain('https://www.example.com/securedrop'))

    def test_server_header_software_present_nginx(self):
        page = mock.Mock()
        page.headers = {'Server': 'nginx/1.6.3'}
        self.assertFalse(validation.validate_server_software(page))

    def test_server_header_software_present_apache(self):
        page = mock.Mock()
        page.headers = {'Server': 'Apache/2.4.10 (Debian)'}
        self.assertFalse(validation.validate_server_software(page))

    def test_server_header_software_not_present(self):
        page = mock.Mock()
        page.headers = {'Server': ''}
        self.assertTrue(validation.validate_server_software(page))

    def test_server_header_version_not_present(self):
        page = mock.Mock()
        page.headers = {'Server': ''}
        self.assertTrue(validation.validate_server_version(page))

    def test_server_header_version_is_present(self):
        page = mock.Mock()
        page.headers = {'Server': 'Apache/2.4.10 (Debian)'}
        self.assertFalse(validation.validate_server_version(page))

    def test_cloudflare_headers_not_present(self):
        page = mock.Mock()
        page.headers = {'Server': ''}
        self.assertTrue(validation.validate_not_using_cdn(page))

    def test_cloudflare_headers_present(self):
        page = mock.Mock()
        page.headers = {'CF-Cache-Status': 'weeee'}
        self.assertFalse(validation.validate_not_using_cdn(page))

    def test_google_analytics_present(self):
        page = mock.Mock()
        page.content = '<script src="analytics.js"></script>'
        self.assertFalse(validation.validate_not_using_analytics(page))

    def test_google_analytics_not_present(self):
        page = mock.Mock()
        page.content = '<h1>My Good SecureDrop Landing Page</h1>'
        self.assertTrue(validation.validate_not_using_analytics(page))

    def test_csp_not_present(self):
        page = mock.Mock()
        page.headers = {'Content-Security-Policy': 'Random Crazy Value'}
        self.assertFalse(validation.validate_csp(page))

    def test_csp_present(self):
        page = mock.Mock()
        page.headers = {'Content-Security-Policy': "default-src 'self'"}
        self.assertTrue(validation.validate_csp(page))

    def test_xss_protection_not_present(self):
        page = mock.Mock()
        page.headers = {'X-XSS-Protection': 'Crazy Value'}
        self.assertFalse(validation.validate_xss_protection(page))

    def test_xss_protection_present(self):
        page = mock.Mock()
        page.headers = {'X-XSS-Protection': '1; mode=block'}
        self.assertTrue(validation.validate_xss_protection(page))

    def test_nosniff_protection_not_present(self):
        page = mock.Mock()
        page.headers = {'X-Content-Type-Options': 'Crazy Value'}
        self.assertFalse(validation.validate_no_sniff(page))

    def test_nosniff_protection_not_present(self):
        page = mock.Mock()
        page.headers = {'X-Content-Type-Options': 'nosniff'}
        self.assertTrue(validation.validate_no_sniff(page))

    def test_no_download_option_not_present(self):
        page = mock.Mock()
        page.headers = {'X-Download-Options': 'open'}
        self.assertFalse(validation.validate_download_options(page))

    def test_no_download_option_present(self):
        page = mock.Mock()
        page.headers = {'X-Download-Options': 'noopen'}
        self.assertTrue(validation.validate_download_options(page))

    def test_clickjacking_protection_not_present(self):
        page = mock.Mock()
        page.headers = {'X-Frame-Options': 'ALLOW'}
        self.assertFalse(validation.validate_clickjacking_protection(page))

    def test_clickjacking_protection_present(self):
        page = mock.Mock()
        page.headers = {'X-Frame-Options': 'DENY'}
        self.assertTrue(validation.validate_clickjacking_protection(page))

    def test_cross_domain_policy_not_set_properly(self):
        page = mock.Mock()
        page.headers = {'X-Permitted-Cross-Domain-Policies': 'Crazy'}
        self.assertFalse(validation.validate_cross_domain_policy(page))

    def test_cross_domain_policy_set_properly(self):
        page = mock.Mock()
        page.headers = {'X-Permitted-Cross-Domain-Policies': 'master-only'}
        self.assertTrue(validation.validate_cross_domain_policy(page))

    def test_pragma_header_not_disabling_caching(self):
        page = mock.Mock()
        page.headers = {'Pragma': 'so-much-cache'}
        self.assertFalse(validation.validate_pragma(page))

    def test_pragma_header_disabling_caching(self):
        page = mock.Mock()
        page.headers = {'Pragma': 'no-cache'}
        self.assertTrue(validation.validate_pragma(page))

    def test_expires_header_not_disabling_caching(self):
        page = mock.Mock()
        page.headers = {'Expires': '10033213'}
        self.assertFalse(validation.validate_expires(page))

    def test_expires_header_disabling_caching(self):
        page = mock.Mock()
        page.headers = {'Expires': '-1'}
        self.assertTrue(validation.validate_expires(page))

    def test_cache_control_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': ''}
        self.assertTrue(validation.validate_cache_control_set(page))

    def test_cache_control_not_set(self):
        page = mock.Mock()
        page.headers = {'Expires': '-1'}
        self.assertFalse(validation.validate_cache_control_set(page))

    def test_cache_control_must_revalidate_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'must-revalidate'}
        self.assertTrue(validation.validate_cache_must_revalidate(page))

    def test_cache_control_must_revalidate_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'must-not-revalidate'}
        self.assertFalse(validation.validate_cache_must_revalidate(page))

    def test_cache_control_validate_nocache_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'no-cache'}
        self.assertTrue(validation.validate_nocache(page))

    def test_cache_control_validate_nocache_not_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'cache'}
        self.assertFalse(validation.validate_nocache(page))

    def test_cache_control_validate_notransform_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'no-transform'}
        self.assertTrue(validation.validate_notransform(page))

    def test_cache_control_validate_notransform_not_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'transform'}
        self.assertFalse(validation.validate_notransform(page))

    def test_cache_control_validate_nostore_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'no-store'}
        self.assertTrue(validation.validate_nostore(page))

    def test_cache_control_validate_nostore_not_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'store'}
        self.assertFalse(validation.validate_nostore(page))

    def test_cache_control_validate_nostore_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'private'}
        self.assertTrue(validation.validate_private(page))

    def test_cache_control_validate_nostore_not_set(self):
        page = mock.Mock()
        page.headers = {'Cache-Control': 'public'}
        self.assertFalse(validation.validate_private(page))
