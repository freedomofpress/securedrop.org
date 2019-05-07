from django.test import TestCase

from blog.tests.factories import BlogPageFactory, BlogIndexPageFactory, CategoryPageFactory


class BlogIndexPageTest(TestCase):
    def setUp(self):
        self.blog_index = BlogIndexPageFactory()
        self.live_post = BlogPageFactory(live=True, parent=self.blog_index)
        self.unpublished_post = BlogPageFactory(live=False, parent=self.blog_index)

    def test_get_posts_should_return_live_posts(self):
        posts = self.blog_index.get_posts()
        self.assertIn(self.live_post, posts)

    def test_get_posts_should_not_return_unpublished_posts(self):
        posts = self.blog_index.get_posts()
        self.assertNotIn(self.unpublished_post, posts)

    def test_get_posts_returns_newest_post_first(self):
        self.live_post.delete()  # not necessary for this test
        BlogPageFactory(publication_datetime='2018-01-01 00:00Z', parent=self.blog_index)
        first = BlogPageFactory(publication_datetime='2018-03-31 00:00Z', parent=self.blog_index)
        BlogPageFactory(publication_datetime='2018-03-01 00:00Z', parent=self.blog_index)
        posts = self.blog_index.get_posts()
        self.assertEqual(first, posts.first())

    def test_get_posts_returns_oldest_post_last(self):
        self.live_post.delete()  # not necessary for this test
        BlogPageFactory(publication_datetime='2018-01-01 00:00Z', parent=self.blog_index)
        BlogPageFactory(publication_datetime='2018-03-31 00:00Z', parent=self.blog_index)
        last = BlogPageFactory(publication_datetime='2015-03-31 00:00Z', parent=self.blog_index)
        BlogPageFactory(publication_datetime='2018-03-01 00:00Z', parent=self.blog_index)
        posts = self.blog_index.get_posts()
        self.assertEqual(last, posts.last())


class CategoryPageTest(TestCase):
    def setUp(self):
        self.blog_index = BlogIndexPageFactory()
        self.category = CategoryPageFactory(parent=self.blog_index)
        self.live_post = BlogPageFactory(live=True, category=self.category, parent=self.blog_index)
        self.unpublished_post = BlogPageFactory(live=False, category=self.category, parent=self.blog_index)
        self.other_category = CategoryPageFactory(parent=self.blog_index)
        self.category_post = BlogPageFactory(parent=self.blog_index, category=self.category)
        self.other_category_post = BlogPageFactory(parent=self.blog_index, category=self.other_category)

    def test_get_posts_should_return_live_posts(self):
        posts = self.category.get_posts()
        self.assertIn(self.live_post, posts)

    def test_get_posts_should_not_return_unpublished_posts(self):
        posts = self.category.get_posts()
        self.assertNotIn(self.unpublished_post, posts)

    def test_get_posts_should_return_posts_in_its_category(self):
        posts = self.category.get_posts()
        self.assertIn(self.category_post, posts)

    def test_get_posts_should_not_return_posts_in_other_category(self):
        posts = self.category.get_posts()
        self.assertNotIn(self.other_category_post, posts)

    def test_get_posts_should_return_siblings(self):
        post = self.category.get_posts().first()
        # Because Wagtail sometimes returns a Page object, and sometimes a BlogIndexPage object, testing via title
        self.assertEqual(self.category.get_parent().title, post.get_parent().title)

    def test_get_posts_returns_newest_post_first(self):
        self.live_post.delete()  # not necessary for this test
        self.category_post.delete()  # not necessary for this test
        BlogPageFactory(publication_datetime='2018-01-01 00:00Z', parent=self.blog_index, category=self.category)
        first = BlogPageFactory(publication_datetime='2018-03-31 00:00Z', parent=self.blog_index, category=self.category)
        BlogPageFactory(publication_datetime='2018-03-01 00:00Z', parent=self.blog_index, category=self.category)
        posts = self.category.get_posts()
        self.assertEqual(first, posts.first())

    def test_get_posts_returns_oldest_post_last(self):
        self.live_post.delete()  # not necessary for this test
        self.category_post.delete()  # not necessary for this test
        BlogPageFactory(publication_datetime='2018-01-01 00:00Z', parent=self.blog_index, category=self.category)
        BlogPageFactory(publication_datetime='2018-03-31 00:00Z', parent=self.blog_index)
        last = BlogPageFactory(publication_datetime='2015-03-31 00:00Z', parent=self.blog_index, category=self.category)
        BlogPageFactory(publication_datetime='2018-03-01 00:00Z', parent=self.blog_index, category=self.category)
        posts = self.category.get_posts()
        self.assertEqual(last, posts.last())
