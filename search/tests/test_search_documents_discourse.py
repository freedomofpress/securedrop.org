import itertools
from unittest import mock
from unittest.mock import DEFAULT

from django.test import TestCase, override_settings
from django.utils.html import strip_tags

from search.models import SearchDocument
from search.utils.discourse import index_all_topics
from search.utils.discourse.client import DiscourseClient


TOPICS_RESPONSE = [
    {
        'id': 0,
        'posts_count': 2,
        'created_at': '2000-01-01 00:00:00',
    },
]

TOPIC_DETAILS = {
    'post_stream': {
        'posts': [
            {
                'id': 1,
                'name': 'Person 1',
                'username': 'username1',
                'cooked': '<p>first content</p>',
            },
            {
                'id': 2,
                'name': 'Person 2',
                'username': 'username2',
                'cooked': '<p>second content</p>',
            },
        ],
        'stream': [1, 2],
    },
    'title': 'Example post title',
}

TOPIC_DETAILS_WITH_EXTRAS = {
    'post_stream': {
        'posts': [
            {
                'id': 1,
                'name': 'Person 1',
                'username': 'username1',
                'cooked': '<p>first content</p>',
            },
            {
                'id': 2,
                'name': 'Person 2',
                'username': 'username2',
                'cooked': '<p>second content</p>',
            },
        ],
        'stream': [1, 2, 3],
    },
    'title': 'Example post title',
}

EXTRA_TOPIC_POSTS = {
    'post_stream': {
        'posts': [
            {
                'id': 3,
                'name': 'Person 3',
                'username': 'username3',
                'cooked': '<p>third content</p>',
            },
        ],
        'stream': [1, 2, 3],
    },
}


@override_settings(DISCOURSE_HOST='example.com')
class IndexTopicsTestCase(TestCase):
    @mock.patch.multiple(DiscourseClient, all_topics=DEFAULT, topic=DEFAULT)
    def setUp(self, all_topics, topic):
        all_topics.return_value = TOPICS_RESPONSE
        topic.return_value = TOPIC_DETAILS
        index_all_topics()
        self.document = SearchDocument.objects.get(key='discourse-topic-0')

    def test_posts_are_searchable_by_content(self):
        self.assertEqual(
            SearchDocument.objects.filter(search_vector='second').count(),
            1,
        )

    def test_posts_are_searchable_by_username(self):
        self.assertEqual(
            SearchDocument.objects.filter(search_vector='username2').count(),
            1,
        )

    def test_posts_are_searchable_by_name(self):
        self.assertEqual(
            SearchDocument.objects.filter(search_vector='Person 1').count(),
            1,
        )

    def test_created_document_title_should_be_post_title(self):
        self.assertEqual(self.document.title, TOPIC_DETAILS['title'])

    def test_created_document_type_should_be_forum(self):
        self.assertEqual(self.document.result_type, 'F')

    def test_created_document_content_should_be_stripped_posts(self):
        list_of_fields = [
            [
                post['name'],
                post['username'],
                strip_tags(post['cooked'])
            ] for post in TOPIC_DETAILS['post_stream']['posts']
        ]

        self.assertEqual(
            self.document.search_content,
            TOPIC_DETAILS['title'] + '\n' +
            '\n'.join(
                itertools.chain(*list_of_fields)
            )
        )

    def test_created_document_has_correct_url(self):
        self.assertEqual(self.document.url, 'https://example.com/t/0')

    def test_created_document_has_posts_count_metadata(self):
        self.assertEqual(self.document.data['posts_count'], '2')

    def test_created_document_has_created_at_metadata(self):
        # the discourse api returns this data as a string
        self.assertEqual(self.document.data['created_at'], '2000-01-01 00:00:00')


@override_settings(DISCOURSE_HOST='example.com')
class IndexTopicsWithExtrasTestCase(TestCase):
    @mock.patch.multiple(DiscourseClient, all_topics=DEFAULT, topic=DEFAULT, posts_for_topic=DEFAULT)
    def setUp(self, all_topics, topic, posts_for_topic):
        all_topics.return_value = TOPICS_RESPONSE
        topic.return_value = TOPIC_DETAILS_WITH_EXTRAS
        posts_for_topic.return_value = EXTRA_TOPIC_POSTS
        index_all_topics()
        self.document = SearchDocument.objects.get(key='discourse-topic-0')

    def test_created_document_should_be_searchable_by_extras(self):
        self.assertEqual(
            SearchDocument.objects.filter(search_vector='third').count(),
            1,
        )

    def test_created_document_content_should_be_stripped_posts_with_extras(self):
        posts_plus_extras = TOPIC_DETAILS['post_stream']['posts'] + EXTRA_TOPIC_POSTS['post_stream']['posts']
        list_of_fields = [
            [
                post['name'],
                post['username'],
                strip_tags(post['cooked'])
            ] for post in posts_plus_extras
        ]

        self.assertEqual(
            self.document.search_content,
            TOPIC_DETAILS['title'] + '\n' +
            '\n'.join(
                itertools.chain(*list_of_fields)
            )
        )
