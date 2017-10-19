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


class CategoryPageTest(TestCase):
    def setUp(self):
        self.blog_index = BlogIndexPageFactory
        self.category = CategoryPageFactory(parent=self.blog_index)
        self.live_post = BlogPageFactory(live=True, category=self.category, parent=self.blog_index)
        self.unpublished_post = BlogPageFactory(live=False, category=self.category, parent=self.blog_index)
        self.other_category = CategoryPageFactory(parent=self.blog_index)
        self.category_post = BlogPageFactory(parent=self.blog_index, category=self.category)
        self.other_category_post = BlogPageFactory(parent=self.blog_index, category=self.other_category)

    def get_posts_should_return_live_posts(self):
        posts = self.category.get_posts()
        self.assertIn(self.live_post, posts)

    def get_posts_should_not_return_unpublished_posts(self):
        posts = self.category.get_posts()
        self.assertNotIn(self.unpublished_post, posts)

    def get_posts_should_return_posts_in_its_category(self):
        posts = self.category.get_posts()
        self.assertIn(self.category_post, posts)

    def get_posts_should_not_return_posts_in_other_category(self):
        posts = self.category.get_posts()
        self.assertNotIn(self.other_category_post, posts)
