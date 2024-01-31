import feedparser
from django.test import Client, TestCase
from blog.tests.factories import BlogIndexPageFactory, BlogPageFactory
from wagtail.models import Site


class RSSTest(TestCase):
    def setUp(self):
        site = Site.objects.get()
        self.blog_index = BlogIndexPageFactory(
            parent=site.root_page,
            search_description="Search me!"
        )
        self.blog_index.save()
        self.blog = BlogPageFactory(parent=self.blog_index)
        BlogPageFactory(parent=self.blog_index)
        self.client = Client()
        response = self.client.get("{}feed/".format(self.blog_index.url))
        self.parsed = feedparser.parse(response.content)

    def test_valid_rss_feed(self):
        # feed.bozo will be 1 if there is an error in the feed
        self.assertEqual(self.parsed.bozo, 0)

    def test_feed_has_correct_title(self):
        expected_title = '{}: {}'.format(
            self.blog_index.get_site().site_name,
            self.blog_index.title
        )
        feed_title = self.parsed.feed.get('title')
        self.assertEqual(expected_title, feed_title)

    def test_feed_has_posts(self):
        # Two posts were created in setup
        self.assertEqual(len(self.parsed.entries), 2)

    def test_feed_has_correct_link(self):
        expected_link = '{}{}'.format(
            self.blog_index.get_site().root_url,
            self.blog_index.url
        )
        self.assertEqual(self.parsed.feed.get('link'), expected_link)

    def test_feed_has_correct_description(self):
        self.assertEqual(self.parsed.feed.get('description'), self.blog_index.search_description)

    def test_feed_has_correct_item_title(self):
        first_post = self.blog_index.get_posts().first()
        self.assertEqual(self.parsed.entries[0].title, first_post.title)

    def test_feed_has_correct_item_link(self):
        first_post = self.blog_index.get_posts().first()
        expected_link = '{}{}'.format(
            self.blog_index.get_site().root_url,
            first_post.url
        )
        self.assertEqual(self.parsed.entries[0].link, expected_link)
