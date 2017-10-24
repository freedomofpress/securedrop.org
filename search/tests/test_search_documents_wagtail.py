from django.test import TestCase

from wagtail.wagtailcore.models import Page

from blog.tests.factories import BlogIndexPageFactory
from home.tests.factories import HomePageFactory
from search.utils.wagtail import (
    KEY_FORMAT,
    index_wagtail_page,
    delete_wagtail_page,
)
from search.models import SearchDocument


class WagtailTestCase(TestCase):

    def setUp(self):
        self.root_page = Page.add_root(instance=Page(title="Root"))
        self.page = HomePageFactory.build()
        self.root_page.add_child(instance=self.page)

    def test_index_wagtail_page(self):
        page = self.page
        index_wagtail_page(page)

        # Assert that a search document was created
        self.assertEqual(
            SearchDocument.objects.filter(key=KEY_FORMAT.format(page.pk)).count(),
            1
        )

    def test_index_wagtail_page_signal(self):
        page = self.page
        page.save_revision()
        page.get_latest_revision().publish()  # trigger page_published signal
        # Assert that a search document was created
        self.assertEqual(
            SearchDocument.objects.filter(key=KEY_FORMAT.format(page.pk)).count(),
            1
        )

    def test_unindex_wagtail_page(self):
        page = self.page
        index_wagtail_page(page)
        delete_wagtail_page(page)
        # Assert that previously created search document was deleted
        self.assertEqual(
            SearchDocument.objects.filter(key=KEY_FORMAT.format(page.pk)).count(),
            0
        )

    def test_unindex_wagtail_page_signal(self):
        page = self.page
        index_wagtail_page(page)
        page.delete()
        # Assert that previously created search document was deleted
        self.assertEqual(
            SearchDocument.objects.filter(key=KEY_FORMAT.format(page.pk)).count(),
            0
        )

    def test_delete_unindexed_page(self):
        """
        Deleting a page should not raise an exception, even if it is
        not indexed

        """

        page = self.page
        try:
            delete_wagtail_page(page)
        except Exception as e:
            self.fail(
                'delete_wagtail_page raised an exception {} ("{}")'.format(
                    type(e).__name__,
                    e.args[0]
                )
            )

    def test_indexed_page_should_have_correct_content(self):
        blog_index = BlogIndexPageFactory(parent=self.page, title="News", body="Some content")
        index_wagtail_page(blog_index)
        self.assertEqual(SearchDocument.objects.get(key=KEY_FORMAT.format(blog_index.pk)).search_content, blog_index.get_search_content())
