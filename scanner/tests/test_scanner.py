import os
import re
from unittest import mock
from datetime import datetime

from django.test import TestCase
from django.utils.timezone import utc
import vcr

from scanner import scanner
from scanner.assets import Asset
from scanner.tests.utils import (
    NON_EXISTENT_URL,
    requests_get_mock,
)
from directory.models import DirectoryEntry
from directory.tests.factories import DirectoryEntryFactory


VCR_DIR = os.path.join(os.path.dirname(__file__), 'scans_vcr')


def long_lasting_cookies(response):
    """modify a HTTP response to extend cookie lifetime"""
    if 'Set-Cookie' in response['headers']:
        timestamp = datetime(2032, 10, 31, 13, 14, 15, tzinfo=utc)
        updated_expiry = re.sub(r'(expires=)([\w, -:]+)', r'\1{}'.format(timestamp.strftime("%a, %d-%b-%y %H:%M:%S %Z")), response['headers']['Set-Cookie'][0])
        response['headers']['Set-Cookie'] = [updated_expiry]
    return response


mod_vcr = vcr.VCR(before_record_response=long_lasting_cookies)


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
    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-not-live.yaml'))
    def test_scan_returns_result_if_site_not_live(self):
        """
        If a site cannot be connected to, scanner should return a ScanResult
        with result.live False

        In addition to vcrpy, this test mocks requests.get to simulate a
        ConnectionError for a URL that does not exist without actually sending
        an HTTP request to that URL
        """
        securedrop = DirectoryEntry(
            title='Freedom of the Press Foundation',
            landing_page_url=NON_EXISTENT_URL,
            onion_address='notreal.onion'
        )
        result = scanner.scan(securedrop)
        self.assertFalse(result.live)

    @mock.patch('scanner.scanner.requests.get', new=requests_get_mock)
    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-not-live.yaml'))
    def test_scan_returns_reurns_url_if_site_not_live(self):
        """
        If a site cannot be connected to, scanner should return a ScanResult
        with the URL attribute set.

        """
        securedrop = DirectoryEntry(
            title='Freedom of the Press Foundation',
            landing_page_url=NON_EXISTENT_URL,
            onion_address='notreal.onion'
        )
        result = scanner.scan(securedrop)
        self.assertEqual(result.landing_page_url, NON_EXISTENT_URL)

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_returns_result_if_site_live(self):
        """
        If a site can be connected to, scanner should return a result with
        result.live True
        """
        securedrop = DirectoryEntry(
            title='Freedom of the Press Foundation',
            landing_page_url='https://securedrop.org',
            onion_address='notreal.onion'
        )
        result = scanner.scan(securedrop)
        self.assertTrue(result.live)

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_result_attributes(self):
        """
        If the site can be connected to, scanner should return a result with
        all its attributes set

        """
        securedrop = DirectoryEntry(
            title='Freedom of the Press Foundation',
            landing_page_url='https://securedrop.org',
            onion_address='notreal.onion'
        )
        result = scanner.scan(securedrop)

        self.assertIsNone(result.forces_https)
        self.assertTrue(result.http_status_200_ok)
        self.assertIsNone(result.hsts)
        self.assertIsNone(result.hsts_max_age)
        self.assertIsNone(result.hsts_entire_domain)
        self.assertIsNone(result.hsts_preloaded)
        self.assertIs(result.subdomain, False)
        self.assertIs(result.no_cookies, True)
        self.assertTrue(result.safe_onion_address)
        self.assertIs(result.no_cdn, False)
        self.assertTrue(result.no_cross_domain_redirects)
        self.assertTrue(result.expected_encoding)
        self.assertTrue(result.no_analytics)
        self.assertTrue(result.no_server_info)
        self.assertTrue(result.no_server_version)
        self.assertTrue(result.csp_origin_only)
        self.assertTrue(result.mime_sniffing_blocked)
        self.assertIs(result.noopen_download, False)
        self.assertTrue(result.xss_protection)
        self.assertIs(result.clickjacking_protection, True)
        self.assertIs(result.good_cross_domain_policy, False)
        self.assertIs(result.http_1_0_caching_disabled, False)
        self.assertIs(result.expires_set, False)
        self.assertTrue(result.cache_control_set)
        self.assertIs(result.cache_control_revalidate_set, False)
        self.assertIs(result.cache_control_nocache_set, False)
        self.assertIs(result.cache_control_notransform_set, False)
        self.assertIs(result.cache_control_nostore_set, False)
        self.assertIs(result.cache_control_private_set, False)
        self.assertIs(result.referrer_policy_set_to_no_referrer, False)
        self.assertIs(result.no_cross_domain_assets, False)
        self.assertNotEqual(result.cross_domain_asset_summary, '')
        self.assertTrue(result.http2)

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scan-site-with-trackers.yaml'))
    def test_scan_detects_presence_of_trackers(self):
        """
        If a site contains common trackers, result.no_analytics should be False
        """
        ap_site = DirectoryEntry(
            title='AP',
            landing_page_url='https://www.ap.org/en-us/',
            onion_address='notreal.onion'
        )
        result = scanner.scan(ap_site)
        self.assertFalse(result.no_analytics)

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scan-site-with-trackers.yaml'))
    def test_scan_detects_presence_of_cross_domain_assets(self):
        """
        If a site contains cross-domain assets, result.no_cross_domain_assets should be False
        """
        ap_site = DirectoryEntry(
            title='AP',
            landing_page_url='https://www.ap.org/en-us/',
            onion_address='notreal.onion'
        )

        result = scanner.scan(ap_site)

        self.assertIs(result.no_cross_domain_assets, False)
        expected_urls = (
            'https://www.googletagmanager.com/ns.html?id=GTM-WS34WVD',
            '//searchg2-assets.crownpeak.net/crownpeak.searchg2-1.0.2.min.js',
            'https://cdn.cookielaw.org/langswitch/ead3872f-33b9-4b16-a7f2-4ea8137893d3.js',
        )

        for url in expected_urls:
            self.assertIn(url, result.cross_domain_asset_summary)

        ignored_urls = (
            'https://www.google-analytics.com/analytics.js',
            'pardot.com/pd.js',
            'https://www.googletagmanager.com/gtm.js?id=',
            'www.crownpeak.com',
            'searchg2.crownpeak.net/',
            'http://www.w3.org/2000/svg',
            'click.bs.carousel.data',
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
            self.assertIn(url, result.ignored_cross_domain_assets)

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scan-site-without-trackers.yaml'))
    def test_scan_detects_absence_of_trackers(self):
        """
        If a site contains no known trackers, result.no_analytics should be True
        """
        fpf_site = DirectoryEntry(
            title='FPF',
            landing_page_url='https://freedom.press/',
            onion_address='notreal.onion'
        )
        result = scanner.scan(fpf_site)
        self.assertTrue(result.no_analytics)

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scrape-securedrop-dot-org.yaml'))
    def test_request_gets_page_if_protocol_identifier_present(self):
        "request_and_scrape_page should handle a URL with a protocol"
        url = 'https://securedrop.org'
        page, soup = scanner.request_and_scrape_page(url)
        self.assertIn('SecureDrop Directory', str(page.content))

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scrape-securedrop-dot-org.yaml'))
    def test_request_gets_page_if_protocol_identifier_not_present(self):
        "request_and_scrape_page should handle a URL without a protocol"
        url = 'securedrop.org'
        page, soup = scanner.request_and_scrape_page(url)
        self.assertIn('SecureDrop Directory', str(page.content))

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_and_commit(self):
        """
        When scanner.scan is called with commit=True, the result of the scan
        should be newly saved to the database and associated with the
        correct DirectoryEntry
        """
        securedrop = DirectoryEntryFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_url='https://securedrop.org',
            onion_address='notreal.onion'
        )
        self.assertEqual(
            0, DirectoryEntry.objects.get(pk=securedrop.pk).results.count()
        )
        scanner.scan(securedrop, commit=True)
        self.assertEqual(
            1, DirectoryEntry.objects.get(pk=securedrop.pk).results.count()
        )

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_and_no_commit(self):
        """
        When scanner.scan is called without commit=True, it should not save
        any results to the database
        """
        securedrop = DirectoryEntryFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_url='https://securedrop.org',
            onion_address='notreal.onion'
        )
        scanner.scan(securedrop)
        self.assertEqual(
            0, DirectoryEntry.objects.get(pk=securedrop.pk).results.count()
        )

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_with_permitted_domains_with_subdomain(self):
        securedrop = DirectoryEntryFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_url='https://securedrop.org',
            onion_address='notreal.onion',
            permitted_domains_for_assets=['analytics.freedom.press'],
        )
        result = scanner.scan(securedrop)
        self.assertEqual(result.no_cross_domain_assets, True)

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'nytimes-tips.yaml'))
    def test_scan_with_permitted_domain(self):
        securedrop = DirectoryEntryFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_url='https://www.nytimes.com/tips',
            onion_address='notreal.onion',
            permitted_domains_for_assets=['nyt.com'],
        )
        result = scanner.scan(securedrop)
        self.assertEqual(result.no_cross_domain_assets, True)

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'bulk-scan.yaml'))
    def test_bulk_scan(self):
        """
        When scanner.bulk_scan is called, it should save all new results to the
        database, associated with the correct DirectoryEntrys
        """
        DirectoryEntryFactory.create(
            title='SecureDrop',
            landing_page_url='https://securedrop.org',
            onion_address='notreal.onion'
        )
        DirectoryEntryFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_url='https://freedom.press',
            onion_address='notreal-2.onion'
        )

        securedrop_pages_qs = DirectoryEntry.objects.all()
        scanner.bulk_scan(securedrop_pages_qs)

        for page in DirectoryEntry.objects.all():
            self.assertEqual(
                1, page.results.count()
            )

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'bulk-scan-error-handling.yaml'))
    def test_bulk_scan_error_handling(self):
        sd1 = DirectoryEntryFactory.create(
            title='SecureDrop',
            landing_page_url='https://www.2600.com/securedrop',
            onion_address='notreal.onion'
        )
        sd2 = DirectoryEntryFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_url='https://www.forbes.com/fdc/securedrop.html',
            onion_address='notreal-2.onion'
        )
        sd3 = DirectoryEntryFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_url='https://www.cnn.com/tips/',
            onion_address='notreal-3.onion'
        )
        self.assertFalse(
            DirectoryEntry.objects.get(pk=sd2.pk).results.exists()
        )
        with mock.patch('scanner.scanner.extract_assets') as extract_assets:
            extract_assets.side_effect = [[], TypeError, []]
            scanner.bulk_scan(DirectoryEntry.objects.all())

        self.assertTrue(
            DirectoryEntry.objects.get(pk=sd1.pk).results.all()[0].live
        )
        self.assertFalse(DirectoryEntry.objects.get(pk=sd2.pk).results.exists())
        self.assertTrue(
            DirectoryEntry.objects.get(pk=sd3.pk).results.all()[0].live
        )

    @mock.patch(
        'scanner.scanner.requests.get',
        new=requests_get_mock
    )
    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'bulk-scan-not-live.yaml'))
    def test_bulk_scan_not_live(self):
        """
        When scanner.bulk_scan is called, it should save all new results to the
        database, even if one of the instances cannot be reached by HTTP. It
        should save a result to the database for the instance that cannot be
        reached by HTTP with live False

        In addition to vcrpy, this test mocks requests.get to simulate a
        ConnectionError for a URL that does not exist without actually sending
        an HTTP request to that URL
        """

        sd1 = DirectoryEntryFactory.create(
            title='SecureDrop',
            landing_page_url='https://securedrop.org',
            onion_address='notreal.onion'
        )
        sd2 = DirectoryEntryFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_url=NON_EXISTENT_URL,
            onion_address='notreal-2.onion'
        )
        sd3 = DirectoryEntryFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_url='https://freedom.press',
            onion_address='notreal-3.onion'
        )

        securedrop_pages_qs = DirectoryEntry.objects.all()
        scanner.bulk_scan(securedrop_pages_qs)

        self.assertTrue(
            DirectoryEntry.objects.get(pk=sd1.pk).results.all()[0].live
        )
        self.assertFalse(
            DirectoryEntry.objects.get(pk=sd2.pk).results.all()[0].live
        )
        self.assertTrue(
            DirectoryEntry.objects.get(pk=sd3.pk).results.all()[0].live
        )

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scrape-sourceanonyme.yaml'))
    def test_forces_https_should_be_none(self):
        domain = 'https://sourceanonyme.radio-canada.ca'

        entry = DirectoryEntryFactory.create(
            title='Source Anonyme',
            landing_page_url=domain,
            onion_address='notreal.onion'
        )
        r = scanner.scan(entry, commit=True)
        self.assertIsNone(r.forces_https)

    @mock.patch('scanner.scanner.requests.get')
    def test_should_call_requests_with_correct_arguments(self, requests_get):
        requests_get.return_value = mock.Mock(content='')
        scanner.request_and_scrape_page(NON_EXISTENT_URL)
        requests_get.assert_called_once_with(
            NON_EXISTENT_URL,
            allow_redirects=True,
            headers={
                'User-Agent': 'SecureDrop Landing Page Scanner 0.1.0',
            },
            timeout=10,
        )


class ScannerRedirectionSuccess(TestCase):
    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-good-redirection.yaml'))
    def test_redirect_target_saved(self):
        entry = DirectoryEntryFactory.create(
            title='SecureDrop',
            landing_page_url='https://httpbin.org/redirect/3',
            onion_address='notreal.onion',
        )

        result = scanner.scan(entry)
        self.assertEqual(result.redirect_target, 'https://httpbin.org/get')

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-permanent-redirection.yaml'))
    def test_permanent_redirect_target_saved(self):
        entry = DirectoryEntryFactory.create(
            title='SecureDrop',
            landing_page_url='https://httpbin.org/redirect-to?status_code=301&url=https%3A%2F%2Fhttpbin.org%2Fget',
            onion_address='notreal.onion',
        )

        result = scanner.scan(entry)
        self.assertEqual(result.redirect_target, 'https://httpbin.org/get')

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-no-redirection.yaml'))
    def test_redirect_target_not_saved_if_not_redirect(self):
        entry = DirectoryEntryFactory.create(
            title='SecureDrop',
            landing_page_url='https://securedrop.org',
            onion_address='notreal.onion',
        )

        result = scanner.scan(entry)
        self.assertIsNone(result.redirect_target)

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-redirection-not-found.yaml'))
    def test_redirection_not_200(self):
        entry = DirectoryEntryFactory.create(
            title='SecureDrop',
            landing_page_url='https://httpbin.org/redirect-to?url=https%3A%2F%2Fhttpbin.org%2Fstatus%2F404',
            onion_address='notreal.onion',
        )

        result = scanner.scan(entry)
        self.assertEqual(result.redirect_target, 'https://httpbin.org/status/404')
        self.assertFalse(result.http_status_200_ok)


class ScannerSubdomainRedirect(TestCase):
    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-subdomain-redirection.yaml'))
    def test_redirect_from_subdomain(self):
        entry = DirectoryEntryFactory.create(
            title='SecureDrop',
            landing_page_url='http://health.nytimes.com',
            onion_address='notreal.onion',
        )
        r = scanner.scan(entry)
        self.assertTrue(r.subdomain)
        self.assertTrue(r.no_cross_domain_redirects)


class ScannerCrossDomainRedirect(TestCase):
    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-cross-domain-redirection.yaml'))
    def test_cross_domain_redirect_detected_and_saved(self):
        entry = DirectoryEntryFactory.create(
            title='SecureDrop',
            landing_page_url='https://httpbin.org/redirect-to?url=http%3A%2F%2Fwww.google.com&status_code=302',
            onion_address='notreal.onion',
        )

        r = scanner.scan(entry)
        self.assertFalse(r.no_cross_domain_redirects)

    @mod_vcr.use_cassette(os.path.join(VCR_DIR, 'scan-with-cross-domain-redirection.yaml'))
    def test_if_cross_domain_redirect_found_continue_to_scan(self):
        """if a cross-domain redirect is found, then we should make a full scan
of target domain"""
        entry = DirectoryEntryFactory.create(
            title='SecureDrop',
            landing_page_url='https://httpbin.org/redirect-to?url=http%3A%2F%2Fwww.google.com&status_code=302',
            onion_address='notreal.onion',
        )
        r = scanner.scan(entry)
        self.assertTrue(r.live)
        self.assertTrue(r.no_cross_domain_assets)


class AssetParsingTest(TestCase):
    def test_should_skip_assets_from_non_domains(self):
        assets = [
            Asset(resource='not-a-domain', kind='img-src', initiator='z.com'),
        ]

        self.assertEqual(
            scanner.parse_assets(assets, ['z.com', 'b.com']),
            {
                'ignored_cross_domain_assets': '',
                'no_cross_domain_assets': True,
                'cross_domain_asset_summary': '',
            }
        )

    def test_should_skip_assets_on_permitted_domains(self):
        assets = [
            Asset(resource='http://a.com/a.gif', kind='img-src', initiator='z.com'),
            Asset(resource='http://b.com/b.gif', kind='img-src', initiator='z.com'),
            Asset(resource='http://z.com/z.gif', kind='img-src', initiator='z.com'),
        ]

        self.assertEqual(
            scanner.parse_assets(assets, ['z.com', 'b.com']),
            {
                'ignored_cross_domain_assets': '',
                'no_cross_domain_assets': False,
                'cross_domain_asset_summary': """z.com\n  * (img-src) http://a.com/a.gif\n"""
            }
        )
