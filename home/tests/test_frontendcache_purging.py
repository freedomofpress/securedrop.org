import datetime

from unittest.mock import patch, call

from django.test import TestCase

from home.tests.factories import HomePageFactory
from github.models import Release
from blog.tests.factories import BlogPageFactory
from directory.tests.factories import DirectoryEntryFactory


@patch('home.signals.purge_page_from_cache')
class FrontendCacheTestCase(TestCase):
    def setUp(self):
        self.home_page = HomePageFactory()

    def test_cache_purged_for_release(self, purge_mock):
        "Homepage cache should be purged when a new release is added"
        Release.objects.create(date=datetime.datetime(2016, 1, 1, 0, 0, 0))
        purge_mock.assert_called_once_with(self.home_page)

    def test_cache_purged_for_blog_post(self, purge_mock):
        "Homepage cache should be purged when a new blog post is added"
        BlogPageFactory.create()
        purge_mock.assert_called_once_with(self.home_page)

    def test_cache_purged_for_directory_entry(self, purge_mock):
        "Homepage cache should be purged when a new directory entry is added"
        DirectoryEntryFactory.create()
        # DirectoryEntry saving logic causes it to be saved twice, triggering
        # the purge twice (this is not necessarily desireable, but it is
        # mostly harmless)
        purge_mock.assert_has_calls([
            call(self.home_page), call(self.home_page)
        ])
