from bs4 import BeautifulSoup

from django.test import TestCase

from wagtail.core.models import Site

from directory.models import DirectorySettings
from directory.tests.factories import (
    DirectoryPageFactory,
    DirectoryEntryFactory,
    ScanResultFactory,
)


class DirectorySettingsTestCase(TestCase):
    @classmethod
    def setUpTestData(self):
        site = Site.objects.get(is_default_site=True)
        self.directory_settings = DirectorySettings.for_site(site)
        self.directory = DirectoryPageFactory(parent=site.root_page)
        self.securedrop_page = DirectoryEntryFactory(parent=self.directory)
        self.result = ScanResultFactory(securedrop=self.securedrop_page)

    def test_scan_disabled_hides_directory_scan_results(self):
        self.directory_settings.show_scan_results = False
        self.directory_settings.save()

        response = self.client.get(self.directory.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        grades = soup.find_all(class_='instance-table__grade-column')

        self.assertEqual(len(grades), 0)

    def test_scan_enabled_shows_directory_scan_results(self):
        self.directory_settings.show_scan_results = True
        self.directory_settings.save()

        response = self.client.get(self.directory.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        grades = soup.find_all(class_='instance-table__grade-column')

        self.assertEqual(len(grades), 1)

    def test_scan_disabled_hides_detail_scan_results(self):
        self.directory_settings.show_scan_results = False
        self.directory_settings.save()

        response = self.client.get(self.securedrop_page.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        grade = soup.find_all(class_='security_grade')
        result = soup.find_all(class_='scan-result')

        self.assertEqual(len(grade), 0)
        self.assertEqual(len(result), 0)

    def test_scan_enabled_shows_detail_scan_results(self):
        self.directory_settings.show_scan_results = True
        self.directory_settings.save()

        response = self.client.get(self.securedrop_page.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        grade = soup.find_all(class_='security_grade')
        result = soup.find_all(class_='scan-result')

        self.assertEqual(len(grade), 1)
        self.assertEqual(len(result), 1)
