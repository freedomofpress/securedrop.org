from urllib.parse import urlparse, urljoin

from django.conf import settings
from django.db import transaction
from django.utils.html import strip_tags

from search.models import SearchDocument
from search.utils.discourse.client import DiscourseClient
from search.utils.search_elements import SearchElements


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

        search_elements = SearchElements()
        search_elements.append(topic_details['title'])

        topic_posts = topic_details['post_stream']['posts']
        post_ids = set(topic_details['post_stream']['stream'])
        for post in topic_posts:
            post_ids.remove(post['id'])
            search_elements.append(post['name'])
            search_elements.append(post['username'])
            search_elements.append(strip_tags(post['cooked']))

        if post_ids:
            extra_topic_posts = client.posts_for_topic(topic['id'], list(post_ids))
            remaining_posts = extra_topic_posts['post_stream']['posts']
            for post in remaining_posts:
                search_elements.append(post['name'])
                search_elements.append(post['username'])
                search_elements.append(strip_tags(post['cooked']))

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
                'search_content': search_elements.as_string(),
                'search_vector': search_elements.as_search_vector(),
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
