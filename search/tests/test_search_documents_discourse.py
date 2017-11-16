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
                'name': 'Person 1',
                'username': 'username1',
                'cooked': '<p>first content</p>',
            },
            {
                'name': 'Person 2',
                'username': 'username2',
                'cooked': '<p>second content</p>',
            },
        ],
    },
    'title': 'Example post title',
}


@override_settings(DISCOURSE_HOST='example.com')
class IndexTopicsTestCase(TestCase):
    @mock.patch.multiple(DiscourseClient, all_topics=DEFAULT, topic=DEFAULT)
    def setUp(self, all_topics, topic):
        all_topics.return_value = TOPICS_RESPONSE
        topic.return_value = TOPIC_DETAILS
        index_all_topics()
        self.document = SearchDocument.objects.get(key='discourse-topic-0')

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
