from datetime import UTC, datetime
from unittest.mock import call, patch

from django.test import TestCase

from blog.models import BlogPage
from blog.tests.factories import CategoryPageFactory
from directory.tests.factories import DirectoryEntryFactory
from github.factories import ProductFactory
from github.models import Release
from home.tests.factories import HomePageFactory


@patch("home.signals.purge_page_from_cache")
class FrontendCacheTestCase(TestCase):
    def setUp(self):
        self.home_page = HomePageFactory()
        self.cat_page = CategoryPageFactory()

    def test_cache_purged_for_release(self, purge_mock):
        "Homepage cache should be purged when a new release is added"
        product = ProductFactory()
        Release.objects.create(
            product=product,
            date=datetime(2016, 1, 1, 0, 0, 0, tzinfo=UTC),
        )
        purge_mock.assert_called_once_with(self.home_page)

    def test_cache_purged_for_blog_post(self, purge_mock):
        "Homepage cache should be purged when a new blog post is added"
        blog_page = BlogPage(
            title="Yet another blog page",
            category=self.cat_page,
            publication_datetime=datetime(2016, 1, 1, 0, 0, 0, tzinfo=UTC),
        )
        self.cat_page.add_child(instance=blog_page)
        purge_mock.assert_called_once_with(self.home_page)

    def test_cache_purged_for_directory_entry(self, purge_mock):
        "Homepage cache should be purged when a new directory entry is added"
        DirectoryEntryFactory.create()
        # DirectoryEntry saving logic causes it to be saved twice, triggering
        # the purge twice (this is not necessarily desireable, but it is
        # mostly harmless)
        purge_mock.assert_has_calls([call(self.home_page), call(self.home_page)])
