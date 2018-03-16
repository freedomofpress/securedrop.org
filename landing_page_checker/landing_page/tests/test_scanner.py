import os
from unittest import mock

from django.test import TestCase
import vcr

from landing_page_checker.landing_page import scanner
from landing_page_checker.landing_page.tests.utils import (
    NON_EXISTENT_URL,
    requests_get_mock,
)
from landing_page_checker.models import SecuredropPage
from landing_page_checker.tests.factories import SecuredropPageFactory


VCR_DIR = os.path.join(os.path.dirname(__file__), 'scans_vcr')


class ScannerTest(TestCase):
    @mock.patch(
        'landing_page_checker.landing_page.scanner.requests.get',
        new=requests_get_mock
    )
    @mock.patch(
        'pshtt.pshtt.requests.get',
        new=requests_get_mock
    )
    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-not-live.yaml'))
    def test_scan_returns_result_if_site_not_live(self):
        securedrop = SecuredropPage(
            title='Freedom of the Press Foundation',
            landing_page_domain=NON_EXISTENT_URL,
            onion_address='notreal.onion'
        )
        result = scanner.scan(securedrop)
        self.assertFalse(result.live)

    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_returns_result_if_site_live(self):
        securedrop = SecuredropPage(
            title='Freedom of the Press Foundation',
            landing_page_domain='https://securedrop.org',
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

    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_and_commit(self):
        securedrop = SecuredropPageFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_domain='https://securedrop.org',
            onion_address='notreal.onion'
        )
        self.assertEqual(
            0, SecuredropPage.objects.get(pk=securedrop.pk).results.count()
        )
        scanner.scan(securedrop, commit=True)
        self.assertEqual(
            1, SecuredropPage.objects.get(pk=securedrop.pk).results.count()
        )

    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
    def test_scan_and_no_commit(self):
        securedrop = SecuredropPageFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_domain='https://securedrop.org',
            onion_address='notreal.onion'
        )
        scanner.scan(securedrop)
        self.assertEqual(
            0, SecuredropPage.objects.get(pk=securedrop.pk).results.count()
        )

    @vcr.use_cassette(os.path.join(VCR_DIR, 'bulk-scan.yaml'))
    def test_bulk_scan(self):
        SecuredropPageFactory.create(
            title='SecureDrop',
            landing_page_domain='https://securedrop.org',
            onion_address='notreal.onion'
        )
        SecuredropPageFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_domain='https://freedom.press',
            onion_address='notreal-2.onion'
        )

        securedrop_pages_qs = SecuredropPage.objects.all()
        scanner.bulk_scan(securedrop_pages_qs)

        for page in SecuredropPage.objects.all():
            self.assertEqual(
                1, page.results.count()
            )

    @mock.patch(
        'landing_page_checker.landing_page.scanner.requests.get',
        new=requests_get_mock
    )
    @mock.patch(
        'pshtt.pshtt.requests.get',
        new=requests_get_mock
    )
    @vcr.use_cassette(os.path.join(VCR_DIR, 'bulk-scan-not-live.yaml'))
    def test_bulk_scan_not_live(self):
        "Scans should save reasonable results even when one site is not live"

        sd1 = SecuredropPageFactory.create(
            title='SecureDrop',
            landing_page_domain='https://securedrop.org',
            onion_address='notreal.onion'
        )
        sd2 = SecuredropPageFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_domain=NON_EXISTENT_URL,
            onion_address='notreal-2.onion'
        )
        sd3 = SecuredropPageFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_domain='https://freedom.press',
            onion_address='notreal-3.onion'
        )

        securedrop_pages_qs = SecuredropPage.objects.all()
        scanner.bulk_scan(securedrop_pages_qs)

        self.assertTrue(
            SecuredropPage.objects.get(pk=sd1.pk).results.all()[0].live
        )
        self.assertFalse(
            SecuredropPage.objects.get(pk=sd2.pk).results.all()[0].live
        )
        self.assertTrue(
            SecuredropPage.objects.get(pk=sd3.pk).results.all()[0].live
        )
