import os
from unittest import mock

from django.test import TestCase
import vcr

from scanner.scanner import perform_scan, request_and_scrape_page
from scanner.tests.utils import (
    NON_EXISTENT_URL,
    requests_get_mock,
)


VCR_DIR = os.path.join(os.path.dirname(__file__), 'scans_vcr')


class ScannerTest(TestCase):
    """
    Tests the landing page scanner. These tests make use of vcrpy, which
    records HTTP responses to YAML cassettes in scans_vcr/ the first time the
    tests are run. Every time after that, it simulates the responses from those
    cassettes, making responses consistent and eliminating the need for a live
    network connection for running tests
    """

    @mock.patch(
        'scanner.scanner.requests.get',
        new=requests_get_mock
    )
    @mock.patch(
        'pshtt.pshtt.requests.get',
        new=requests_get_mock
    )
    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-not-live.yaml'))
    def test_scan_returns_result_if_site_not_live(self):
        """
        If a site cannot be connected to, scanner should return a ScanResult
        with result.live False

        In addition to vcrpy, this test mocks requests.get to simulate a
        ConnectionError for a URL that does not exist without actually sending
        an HTTP request to that URL
        """
        result = perform_scan(NON_EXISTENT_URL)
        self.assertFalse(result['live'])

    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_returns_result_if_site_live(self):
        """
        If a site can be connected to, scanner should return a result with
        result.live True
        """
        result = perform_scan('https://securedrop.org')
        self.assertTrue(result['live'])

    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_result_attributes(self):
        """
        If the site can be connected to, scanner should return a result with
        all its attributes set

        """
        result = perform_scan('https://securedrop.org')

        self.assertTrue(result['forces_https'])
        self.assertTrue(result['http_status_200_ok'])
        self.assertTrue(result['hsts'])
        self.assertTrue(result['hsts_max_age'])
        self.assertTrue(result['hsts_entire_domain'])
        self.assertTrue(result['hsts_preloaded'])
        self.assertIs(result['subdomain'], False)
        self.assertIs(result['no_cookies'], False)
        self.assertTrue(result['safe_onion_address'])
        self.assertIs(result['no_cdn'], False)
        self.assertTrue(result['no_cross_domain_redirects'])
        self.assertTrue(result['expected_encoding'])
        self.assertTrue(result['no_analytics'])
        self.assertTrue(result['no_server_info'])
        self.assertTrue(result['no_server_version'])
        self.assertTrue(result['csp_origin_only'])
        self.assertTrue(result['mime_sniffing_blocked'])
        self.assertIs(result['noopen_download'], False)
        self.assertTrue(result['xss_protection'])
        self.assertIs(result['clickjacking_protection'], False)
        self.assertIs(result['good_cross_domain_policy'], False)
        self.assertIs(result['http_1_0_caching_disabled'], False)
        self.assertIs(result['expires_set'], False)
        self.assertTrue(result['cache_control_set'])
        self.assertIs(result['cache_control_revalidate_set'], False)
        self.assertIs(result['cache_control_nocache_set'], False)
        self.assertIs(result['cache_control_notransform_set'], False)
        self.assertIs(result['cache_control_nostore_set'], False)
        self.assertIs(result['cache_control_private_set'], False)
        self.assertIs(result['referrer_policy_set_to_no_referrer'], False)
        self.assertIs(result['no_cross_domain_assets'], False)
        self.assertNotEqual(result['cross_domain_asset_summary'], '')

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scan-site-with-trackers.yaml'))
    def test_scan_detects_presence_of_trackers(self):
        """
        If a site contains common trackers, result.no_analytics should be False
        """
        result = perform_scan('https://www.ap.org/en-us/')
        self.assertFalse(result['no_analytics'])

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scan-site-with-trackers.yaml'))
    def test_scan_detects_presence_of_cross_domain_assets(self):
        """
        If a site contains cross-domain assets, result.no_cross_domain_assets should be False
        """
        result = perform_scan('https://www.ap.org/en-us/')

        self.assertIs(result['no_cross_domain_assets'], False)
        expected_urls = (
            'https://www.googletagmanager.com/ns.html?id=GTM-TSGB826',
            '//searchg2-assets.crownpeak.net/crownpeak.searchg2-1.0.2.min.js',
            'https://cdn.cookielaw.org/langswitch/ead3872f-33b9-4b16-a7f2-4ea8137893d3.js',
        )

        for url in expected_urls:
            self.assertIn(url, result['cross_domain_asset_summary'])

        ignored_urls = (
            'https://www.google-analytics.com/analytics.js',
            'pardot.com/pd.js',
            'https://www.googletagmanager.com/gtm.js?id=',
            'www.crownpeak.com',
            'searchg2.crownpeak.net/',
            'http://www.w3.org/2000/svg',
            'click.bs.carousel.data',
            'item.active',
            'click.bs.collapse.data',
            'element.id',
            'click.bs.modal.data',
            'hidden.bs.tab',
            'shown.bs.tab',
            'bs.tab',
            'hide.bs.tab',
            'show.bs.tab',
            'click.bs.tab.data',
        )
        for url in ignored_urls:
            self.assertIn(url, result['ignored_cross_domain_assets'])

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scan-site-without-trackers.yaml'))
    def test_scan_detects_absence_of_trackers(self):
        """
        If a site contains no known trackers, result.no_analytics should be True
        """
        result = perform_scan('https://freedom.press/')
        self.assertTrue(result['no_analytics'])

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scrape-securedrop-dot-org.yaml'))
    def test_request_gets_page_if_protocol_identifier_present(self):
        "request_and_scrape_page should handle a URL with a protocol"
        url = 'https://securedrop.org'
        page, soup = request_and_scrape_page(url)
        self.assertIn('SecureDrop Directory', str(page.content))

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scrape-securedrop-dot-org.yaml'))
    def test_request_gets_page_if_protocol_identifier_not_present(self):
        "request_and_scrape_page should handle a URL without a protocol"
        url = 'securedrop.org'
        page, soup = request_and_scrape_page(url)
        self.assertIn('SecureDrop Directory', str(page.content))

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scrape-sourceanonyme.yaml'))
    def test_forces_https_should_not_be_none(self):
        domain = 'https://sourceanonyme.radio-canada.ca'
        r = perform_scan(domain)
        self.assertIsNotNone(r['forces_https'])


class ScannerRedirectionSuccess(TestCase):
    @vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-good-redirection.yaml'))
    def test_redirect_target_saved(self):
        result = perform_scan('https://httpbin.org/redirect/3')
        self.assertEqual(result['redirect_target'], 'https://httpbin.org/get')

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-permanent-redirection.yaml'))
    def test_permanent_redirect_target_saved(self):
        result = perform_scan('https://httpbin.org/redirect-to?status_code=301&url=https%3A%2F%2Fhttpbin.org%2Fget')
        self.assertEqual(result['redirect_target'], 'https://httpbin.org/get')

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-no-redirection.yaml'))
    def test_redirect_target_not_saved_if_not_redirect(self):
        result = perform_scan('https://securedrop.org')
        self.assertNotIn('redirect_target', result)

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-redirection-not-found.yaml'))
    def test_redirection_not_200(self):
        result = perform_scan('https://httpbin.org/redirect-to?url=https%3A%2F%2Fhttpbin.org%2Fstatus%2F404')
        self.assertEqual(result['redirect_target'], 'https://httpbin.org/status/404')
        self.assertFalse(result['http_status_200_ok'])


class ScannerSubdomainRedirect(TestCase):
    @vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-subdomain-redirection.yaml'))
    def test_redirect_from_subdomain(self):
        r = perform_scan('http://health.nytimes.com')
        self.assertTrue(r['subdomain'])
        self.assertTrue(r['no_cross_domain_redirects'])


class ScannerCrossDomainRedirect(TestCase):
    @vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-cross-domain-redirection.yaml'))
    def test_cross_domain_redirect_detected_and_saved(self):
        url = 'https://httpbin.org/redirect-to?url=http%3A%2F%2Fwww.google.com&status_code=302'
        r = perform_scan(url)
        self.assertFalse(r['no_cross_domain_redirects'])
