from datetime import datetime, timezone
from unittest.mock import patch

from django.test import TestCase

from github.models import Release


class FrontendCacheTestCase(TestCase):
    @patch('github.signals.purge_all_from_cache')
    def test_cache_purge__new_release(self, purge_mock):
        "Creating a new release should purge the entire zone"
        Release.objects.create(date=datetime(2018, 4, 25, 0, 0, 0, tzinfo=timezone.utc))
        self.assertEqual(purge_mock.call_count, 1)

    def test_cache_purge__delete_release(self):
        "Deleting a release should purge the entire zone"
        release = Release.objects.create(
            date=datetime(2018, 4, 25, 0, 0, 0, tzinfo=timezone.utc)
        )

        with patch('github.signals.purge_all_from_cache') as purge_mock:
            release.delete()
            self.assertEqual(purge_mock.call_count, 1)

    def test_cache_purge__edit_release(self):
        "Changing a release should purge the entire zone"
        release = Release.objects.create(
            date=datetime(2018, 4, 25, 0, 0, 0, tzinfo=timezone.utc)
        )

        release.url = 'http://notarealwebsite.com'
        with patch('github.signals.purge_all_from_cache') as purge_mock:
            release.save()
            self.assertEqual(purge_mock.call_count, 1)
