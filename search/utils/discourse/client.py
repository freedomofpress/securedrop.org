import logging
import time

import requests


logger = logging.getLogger(__name__)


class DiscourseClient(object):
    """
    A basic Discourse API client. Written to meet our functionality needs, and
    consequently does not cover the full Discourse API surface as documented
    at http://docs.discourse.org/, but it should be fairly easy to add new
    methods as needed.

    """

    def __init__(self, host: str, api_key: str, secure=True):
        self._host = host
        self._api_key = api_key
        self._secure = secure
        # number of seconds to wait after receiving HTTP 429 Too Many Requests
        self._sleep_time = 30

    def _request(self, method: str, path: str, data={}, retries=3) -> dict:

        request_url = '{protocol}{host}{path}'.format(
            protocol='https://' if self._secure else 'http://',
            host=self._host,
            path=path
        )

        data_ = {
            'api_key': self._api_key
        }
        data_.update(data)

        while retries > 0:
            try:
                logger.debug('DiscourseClient requesting {} {} with {}'.format(
                    method, request_url, data_
                ))
                r = requests.request(method, request_url, data=data_)
                r.raise_for_status()
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout) as e:
                retries -= 1
                if not retries:
                    raise
                continue
            except requests.exceptions.HTTPError as e:
                retries -= 1
                if not retries:
                    raise
                if e.response is not None and e.response.status_code == 429:
                    # If we get Too Many Requests, let the server cool off
                    logger.debug(
                        'DiscourseClient received response 429. '
                        'Sleeping for {} seconds'.format(self._sleep_time)
                    )
                    time.sleep(30)
                continue
            return r.json()

    def _get(self, *args, **kwargs) -> dict:
        return self._request('GET', *args, **kwargs)

    def latest(self, page=0) -> dict:
        return self._get('/latest.json', data={'page': page})

    def topic(self, topic_id: int) -> dict:
        return self._get('/t/{}.json'.format(topic_id))

    def posts_for_topic(self, topic_id: int, post_ids: int) -> dict:
        """Returns the posts for the given IDs within the given topic"""
        path = '/t/{topic_id}/posts.json?{post_ids}'.format(
            topic_id=topic_id,
            post_ids=''.join(
                'post_ids[]={}&'.format(str(i))
                for i in post_ids
            )[:-1]
        )
        return self._get(path)

    def all_topics(self) -> list:
        """
        Convenience method to paginate through all of the latest endpoint to
        return a complete list of topics. Results in multiple API requests.

        Unlike single-request API methods, this returns a flat list of topics
        instead of a complete response data dict.

        """

        page = 0
        topics = []
        keep_going = True
        while keep_going:
            data = self.latest(page=page)
            topics = topics + data['topic_list']['topics']
            page = page + 1
            # Check if there's a next page
            if 'more_topics_url' not in data['topic_list']:
                keep_going = False

        return topics
