from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from wagtail.core.models import Site

from directory.models.entry import DirectoryEntry
from directory.warnings import WARNINGS
from directory.tests.factories import (
    DirectoryEntryFactory,
    DirectoryPageFactory,
    ScanResultFactory,
)


class DirectoryChoicesTest(TestCase):
    def test_all_warnings_can_be_chosen(self):
        all_warning_names = set(warning.name for warning in WARNINGS)
        warning_choice_names = set(
            choice[0] for choice in DirectoryEntry.WARNING_CHOICES
        )

        self.assertEqual(all_warning_names, warning_choice_names)


class DirectoryNoResultsTest(TestCase):
    def setUp(self):
        site = Site.objects.get()
        self.entry = DirectoryEntryFactory(
            parent=DirectoryPageFactory(parent=site.root_page)
        )

    def test_warnings_if_no_scan_results_exist(self):
        response = self.client.get(self.entry.url)
        self.assertEqual(response.status_code, 200)


class DirectoryNoWarningTest(TestCase):
    def setUp(self):
        site = Site.objects.get()
        self.entry = DirectoryEntryFactory(
            parent=DirectoryPageFactory(parent=site.root_page)
        )
        self.result = ScanResultFactory(
            securedrop=self.entry,
            landing_page_url=self.entry.landing_page_url,
            no_failures=True,
        )
        self.result.save()
        self.entry.save()

        self.client = Client()

    def test_page_request_should_succeed_if_no_warnings_on_result(self):
        response = self.client.get(self.entry.url)
        self.assertEqual(response.status_code, 200)


class DirectoryPinnedWarningTest(TestCase):
    def setUp(self):
        site = Site.objects.get()
        self.entry = DirectoryEntryFactory(
            parent=DirectoryPageFactory(parent=site.root_page)
        )
        self.result = ScanResultFactory(
            securedrop=self.entry,
            landing_page_url=self.entry.landing_page_url,
            no_failures=True,
        )
        self.result.save()
        self.entry.save()

        self.client = Client()

    def test_warning_presence(self):
        """warning should be displayed if pinned"""
        self.entry.warnings_pinned = ['unreachable_landing_page']
        self.entry.save()
        response = self.client.get(self.entry.url)
        self.assertContains(
            response,
            "This SecureDrop's landing page appears to be unreachable. You may wish to wait until the landing page is back online before contacting this SecureDrop, so you can verify the .onion address.",
        )

    def test_pinning_and_ignoring_the_same_warning_is_invalid(self):
        self.entry.warnings_pinned = ['unreachable_landing_page']
        self.entry.warnings_ignored = ['unreachable_landing_page']
        with self.assertRaises(ValidationError):
            self.entry.save()


class DirectoryModerateWarningTest(TestCase):
    def setUp(self):
        site = Site.objects.get()
        self.entry = DirectoryEntryFactory(
            parent=DirectoryPageFactory(parent=site.root_page)
        )
        self.result = ScanResultFactory(
            securedrop=self.entry,
            landing_page_url=self.entry.landing_page_url,
            moderate_warning=True,
        )
        self.result.save()
        self.entry.save()

        self.client = Client()

    def test_warning_presence(self):
        """warning should always be displayed"""
        response = self.client.get(self.entry.url)
        self.assertContains(
            response,
            'We recommend only visiting this SecureDrop landing page <a href="https://www.torproject.org/download/download-easy.html.en">using the Tor browser</a>.',
            status_code=200,
        )

    def test_warning_message_suppressed_if_page_ignores_all_triggered_warnings(self):
        self.entry.warnings_ignored = ['safe_onion_address']
        self.entry.save()

        response = self.client.get(self.entry.url)

        self.assertNotContains(
            response,
            'We recommend only visiting this SecureDrop landing page <a href="https://www.torproject.org/download/download-easy.html.en">using the Tor browser</a>.',
            status_code=200,
        )

    def test_single_warning_message_suppressed_if_page_ignores_that_warning(self):
        self.result.subdomain = True
        self.result.save()
        self.entry.warnings_ignored = ['safe_onion_address']
        self.entry.save()

        response = self.client.get(self.entry.url)
        self.assertContains(
            response,
            'is hosted on a subdomain',
            status_code=200,
        )

        self.assertNotContains(
            response,
            'includes a clickable link to a Tor Onion Service',
            status_code=200,
        )


class DirectorySevereWarningTest(TestCase):
    def setUp(self):
        site = Site.objects.get()
        self.entry = DirectoryEntryFactory(
            parent=DirectoryPageFactory(parent=site.root_page)
        )
        self.result = ScanResultFactory(
            securedrop=self.entry,
            landing_page_url=self.entry.landing_page_url,
            severe_warning=True,
        )
        self.result.save()
        self.entry.save()

        self.client = Client()

    def test_warning_presence(self):
        """warning should be displayed if warnings flag in request"""
        response = self.client.get(self.entry.url)
        self.assertContains(
            response,
            'We strongly advise you to only visit this landing page <a href="https://www.torproject.org/download/download-easy.html.en">using the Tor browser</a>, with the <a href="https://tb-manual.torproject.org/en-US/security-slider.html">security slider</a> set to "safest".',
            status_code=200,
        )

    def test_warning_message_suppressed_if_page_ignores_all_triggered_warnings(self):
        self.entry.warnings_ignored = ['no_third_party_assets']
        self.entry.save()
        self.entry.refresh_from_db()
        response = self.client.get(self.entry.url)
        self.assertNotContains(
            response,
            'We strongly advise you to only visit this landing page <a href="https://www.torproject.org/download/download-easy.html.en">using the Tor browser</a>, with the <a href="https://tb-manual.torproject.org/en-US/security-slider.html">security slider</a> set to "safest".',
            status_code=200,
        )


class DirectoryUnreachableWarningTest(TestCase):
    def setUp(self):
        site = Site.objects.get()
        self.entry = DirectoryEntryFactory(
            parent=DirectoryPageFactory(parent=site.root_page)
        )
        self.result = ScanResultFactory(
            securedrop=self.entry,
            landing_page_url=self.entry.landing_page_url,
            no_failures=True,
        )
        self.client = Client()

    def test_warning_presence(self):
        self.result.http_status_200_ok = False
        self.result.save()
        response = self.client.get(self.entry.url)
        self.assertContains(
            response,
            "This SecureDrop's landing page appears to be unreachable",
            status_code=200,
        )
        self.assertContains(
            response,
            'images/instance-status/Error.svg'
        )
