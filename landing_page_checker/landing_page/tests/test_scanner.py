import os

from django.test import TestCase
import vcr

from landing_page_checker.landing_page import scanner
from landing_page_checker.models import SecuredropPage


VCR_DIR = os.path.join(os.path.dirname(__file__), 'scans_vcr')


class ScannerTest(TestCase):
    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-not-live.yaml'))
    def test_scan_returns_result_if_site_not_live(self):
        securedrop = SecuredropPage(
            title='Freedom of the Press Foundation',
            landing_page_domain='notarealsite.party',
            onion_address='notreal.onion'
        )
        result = scanner.scan(securedrop)
        self.assertFalse(result.live)

    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_returns_result_if_site_live(self):
        securedrop = SecuredropPage(
            title='Freedom of the Press Foundation',
            landing_page_domain='securedrop.org',
            onion_address='notreal.onion'
        )
        result = scanner.scan(securedrop)
        self.assertTrue(result.live)

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scrape-securedrop-dot-org.yaml'))
    def test_request_gets_page_if_protocol_identifier_present(self):
        url = 'https://securedrop.org'
        page, soup = scanner.request_and_scrape_page(url)
        self.assertIn('SecureDrop Directory', str(page.content))

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scrape-securedrop-dot-org.yaml'))
    def test_request_gets_page_if_protocol_identifier_not_present(self):
        url = 'securedrop.org'
        page, soup = scanner.request_and_scrape_page(url)
        self.assertIn('SecureDrop Directory', str(page.content))
