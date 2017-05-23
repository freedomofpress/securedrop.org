from bs4 import BeautifulSoup
import os
from unittest import mock

from django.test import TestCase
import vcr

from directory.landing_page import scanner
from directory.models import Securedrop, Result


VCR_DIR = os.path.join(os.path.dirname(__file__), 'scans_vcr')


class ScannerTest(TestCase):
    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-not-live.yaml'))
    def test_scan_returns_result_if_site_not_live(self):
        securedrop = Securedrop(organization='Freedom of the Press Foundation',
                                landing_page_domain='notarealsite.party',
                                onion_address='notreal.onion')
        result = scanner.scan(securedrop)
        self.assertFalse(result.live)

    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_returns_result_if_site_live(self):
        securedrop = Securedrop(organization='Freedom of the Press Foundation',
                                landing_page_domain='securedrop.org',
                                onion_address='notreal.onion')
        result = scanner.scan(securedrop)
        self.assertTrue(result.live)

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scrape-securedrop-dot-org.yaml'))
    def test_clean_url_successfully_strips_off_protocol_identifier(self):
        url = 'https://securedrop.org'
        self.assertEqual(scanner.clean_url(url), 'securedrop.org')

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

    @vcr.use_cassette(os.path.join(VCR_DIR, 'pshtt-result-securedrop-dot-org.yaml'))
    def test_pshtt_command_outputs_formatted_json(self):
        url = 'securedrop.org'
        pshtt_results = scanner.pshtt(url)
        self.assertTrue(pshtt_results['HSTS'])

    @vcr.use_cassette(os.path.join(VCR_DIR, 'pshtt-result-site-not-live.yaml'))
    def test_pshtt_command___live_is_false__if__site_not_live(self):
        url = 'www.notarealsiteeeeeeee.com'
        pshtt_results = scanner.pshtt(url)
        self.assertFalse(pshtt_results['Live'])
