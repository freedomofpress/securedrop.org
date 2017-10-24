import json
from django.test import TestCase

from blog.tests.factories import BlogIndexPageFactory, BlogPageFactory


class TestBlogIndex(TestCase):
    def setUp(self):
        self.title = 'Awesome'
        self.body = 'Cool'
        self.blog_index = BlogIndexPageFactory(
            title=self.title,
            body=json.dumps([
                {'type': 'rich_text', 'value': self.body}
            ])
        )
        self.blog_title = 'Blog'
        self.blog_page = BlogPageFactory(title='Blog', parent=self.blog_index)
        self.search_content = self.blog_index.get_search_content()

    def test_get_search_content_indexes_title(self):
        self.assertIn(self.title, self.search_content)

    def test_get_search_content_indexes_body(self):
        print(self.search_content)
        self.assertIn(self.body, self.search_content)

    def test_get_search_content_index_blog_page_titles(self):
        self.assertIn(self.blog_title, self.search_content)


class TestBlogPage(TestCase):
    def setUp(self):
        self.title = 'Awesome'
        self.body = 'Cool'
        self.teaser_text = 'Best blog'
        blog_index = BlogIndexPageFactory()
        self.blog = BlogPageFactory(
            title=self.title,
            body=json.dumps([
                {'type': 'text', 'value': self.body}
            ]),
            parent=blog_index,
            teaser_text=self.teaser_text,
        )
        self.search_content = self.blog.get_search_content()

    def test_get_search_content_indexes_title(self):
        self.assertIn(self.title, self.search_content)

    def test_get_search_content_indexes_body(self):
        self.assertIn(self.body, self.search_content)

    def test_get_search_content_indexes_category_page_title(self):
        self.assertIn(self.blog.category.title, self.search_content)

    def test_get_search_content_indexes_teaser_text(self):
        self.assertIn(self.teaser_text, self.search_content)
