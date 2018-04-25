import datetime

from unittest.mock import patch

from django.test import TestCase

from github.models import Release


@patch('github.signals.purge_all_from_cache')
class FrontendCacheTestCase(TestCase):
    def test_cache_purge__new_release(self, purge_mock):
        "Creating a new release should purge the entire zone"
        Release.objects.create(date=datetime.datetime(2018, 4, 25, 0, 0, 0))
        purge_mock.assert_called_once()

    def test_cache_purge__delete_release(self, purge_mock):
        "Deleting a release should purge the entire zone"
        release = Release.objects.create(
            date=datetime.datetime(2018, 4, 25, 0, 0, 0)
        )
        purge_mock.reset()

        release.delete()
        purge_mock.assert_called_once()

    def test_cache_purge__edit_release(self, purge_mock):
        "Changing a release should purge the entire zone"
        release = Release.objects.create(
            date=datetime.datetime(2018, 4, 25, 0, 0, 0)
        )
        purge_mock.reset()

        release.url = 'http://notarealwebsite.com'
        release.save()
        purge_mock.assert_called_once()
