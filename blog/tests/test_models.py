from django.test import TestCase

from blog.tests.factories import BlogPageFactory, BlogIndexPageFactory, CategoryPageFactory

class BlogIndexPageTest(TestCase):
    def setUp(self):
        self.blog_index = BlogIndexPageFactory
        self.live_post = BlogPageFactory(live=True, parent=self.blog_index)
        self.unpublished_post = BlogPageFactory(live=False, parent=self.blog_index)

    def get_posts_should_return_live_posts(self):
        posts = self.blog_index.get_posts()
        self.assertIn(self.live_post, posts)

    def get_posts_should_not_return_unpublished_posts(self):
        posts = self.blog_index.get_posts()
        self.assertNotIn(self.unpublished_post, posts)

