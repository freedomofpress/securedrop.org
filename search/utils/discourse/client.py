import requests


class DiscourseClient(object):
    """
    A basic Discourse API client. Written to meet our functionality needs, and
    consequently does not cover the full Discourse API surface as documented
    at http://docs.discourse.org/, but it should be fairly easy to add new
    methods as needed.

    """

    def __init__(self, host, api_key, secure=True):
        self._host = host
        self._api_key = api_key
        self._secure = secure

    def _request(self, method, path, data={}):

        request_url = '{protocol}{host}{path}'.format(
            protocol='https://' if self._secure else 'http://',
            host=self._host,
            path=path
        )

        data_ = {
            'api_key': self._api_key
        }
        data_.update(data)

        r = requests.request(
            method,
            request_url,
            data=data_
        )

        return r.json()

    def _get(self, *args, **kwargs):
        return self._request('GET', *args, **kwargs)

    def latest(self, page=0):
        return self._get('/latest.json', data={'page': page})

    def topic(self, topic_id):
        return self._get('/t/{}.json'.format(topic_id))

    def all_topics(self):
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
