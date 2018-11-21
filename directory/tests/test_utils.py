from unittest import mock

from django.test import TestCase

from directory.models import DirectoryEntry
from directory.tests.factories import DirectoryEntryFactory
from directory.tests.utils import (
    NON_EXISTENT_URL,
    perform_scan_mock,
)
from directory.utils import scan, bulk_scan


class TestScanningUtils(TestCase):
    @mock.patch('directory.utils.perform_scan', new=perform_scan_mock)
    def test_scan_and_commit(self):
        """
        When scan is called with commit=True, the result of the scan
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
        scan(securedrop, commit=True)

        self.assertEqual(
            1, DirectoryEntry.objects.get(pk=securedrop.pk).results.count()
        )

    @mock.patch('directory.utils.perform_scan', new=perform_scan_mock)
    def test_scan_and_no_commit(self):
        """
        When scan is called without commit=True, it should not save
        any results to the database
        """
        securedrop = DirectoryEntryFactory.create(
            title='Freedom of the Press Foundation',
            landing_page_url='https://securedrop.org',
            onion_address='notreal.onion'
        )
        scan(securedrop)
        self.assertEqual(
            0, DirectoryEntry.objects.get(pk=securedrop.pk).results.count()
        )

    @mock.patch('directory.utils.perform_scan', new=perform_scan_mock)
    def test_bulk_scan(self):
        """
        When bulk_scan is called, it should save all new results to the
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
        bulk_scan(securedrop_pages_qs)

        for page in DirectoryEntry.objects.all():
            self.assertEqual(
                1, page.results.count()
            )

    @mock.patch('directory.utils.perform_scan', new=perform_scan_mock)
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
        bulk_scan(securedrop_pages_qs)

        self.assertTrue(
            DirectoryEntry.objects.get(pk=sd1.pk).results.all()[0].live
        )
        self.assertFalse(
            DirectoryEntry.objects.get(pk=sd2.pk).results.all()[0].live
        )
        self.assertTrue(
            DirectoryEntry.objects.get(pk=sd3.pk).results.all()[0].live
        )
