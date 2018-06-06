import os
from unittest import mock

from django.test import TestCase
import vcr

from scanner import scanner
from scanner.tests.utils import (
    NON_EXISTENT_URL,
    requests_get_mock,
)
from directory.models import DirectoryEntry
from directory.tests.factories import DirectoryEntryFactory


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
        securedrop = DirectoryEntry(
            title='Freedom of the Press Foundation',
            landing_page_url=NON_EXISTENT_URL,
            onion_address='notreal.onion'
        )
        result = scanner.scan(securedrop)
        self.assertFalse(result.live)

    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
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

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scan-site-with-trackers.yaml'))
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

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scan-site-without-trackers.yaml'))
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

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scrape-securedrop-dot-org.yaml'))
    def test_request_gets_page_if_protocol_identifier_present(self):
        "request_and_scrape_page should handle a URL with a protocol"
        url = 'https://securedrop.org'
        page, soup = scanner.request_and_scrape_page(url)
        self.assertIn('SecureDrop Directory', str(page.content))

    @vcr.use_cassette(os.path.join(VCR_DIR, 'scrape-securedrop-dot-org.yaml'))
    def test_request_gets_page_if_protocol_identifier_not_present(self):
        "request_and_scrape_page should handle a URL without a protocol"
        url = 'securedrop.org'
        page, soup = scanner.request_and_scrape_page(url)
        self.assertIn('SecureDrop Directory', str(page.content))

    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
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

    @vcr.use_cassette(os.path.join(VCR_DIR, 'full-scan-site-live.yaml'))
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

    @vcr.use_cassette(os.path.join(VCR_DIR, 'bulk-scan.yaml'))
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

    @mock.patch(
        'scanner.scanner.requests.get',
        new=requests_get_mock
    )
    @mock.patch(
        'pshtt.pshtt.requests.get',
        new=requests_get_mock
    )
    @vcr.use_cassette(os.path.join(VCR_DIR, 'bulk-scan-not-live.yaml'))
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
