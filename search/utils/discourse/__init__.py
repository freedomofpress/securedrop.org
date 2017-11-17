from urllib.parse import urlparse, urljoin

from django.conf import settings
from django.db import transaction
from django.utils.html import strip_tags

from search.models import SearchDocument
from search.utils.discourse.client import DiscourseClient


KEY_FORMAT = 'discourse-topic-{}'


@transaction.atomic
def index_all_topics():
    client = DiscourseClient(
        settings.DISCOURSE_HOST,
        settings.DISCOURSE_API_KEY
    )

    # Get all topics
    topics = client.all_topics()
    results = []

    for topic in topics:
        topic_details = client.topic(topic['id'])

        searchable_content = [topic_details['title']]

        # TODO: This only gets the most recent 20 posts on the topic, because
        # I could not figure out how to do better with the discourse API. If
        # there's a way to get all of them, update the API with the appropriate
        # methods and use them here.
        topic_posts = topic_details['post_stream']['posts']
        post_ids = set(topic_details['post_stream']['stream'])
        for post in topic_posts:
            post_ids.remove(post['id'])
            searchable_content = searchable_content + [
                post['name'],
                post['username'],
                strip_tags(post['cooked']),
            ]

        if post_ids:
            remaining_posts = client.posts_for_topic(topic['id'], list(post_ids))
            print('remaining posts', post_ids)
            print(remaining_posts)
        # Create or update the document
        document_key = KEY_FORMAT.format(topic['id'])

        url = urljoin(
            urlparse(
                '//' + settings.DISCOURSE_HOST,
                'https' if client._secure else 'http',
            ).geturl(),
            '/'.join(['t', str(topic['id'])]),
        )
        # this is the only part that should be @transaction.atomic.. imo
        result = SearchDocument.objects.update_or_create(
            {
                'title': topic_details['title'],
                'url': url,
                'search_content': '\n'.join(searchable_content),
                'data': {
                    'posts_count': topic['posts_count'],
                    'created_at': topic['created_at'],
                },
                'result_type': 'F',
                'key': document_key,
            },
            key=document_key
        )
        results.append(result)

    return results
