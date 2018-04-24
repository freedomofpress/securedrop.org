from unittest.mock import patch

from django.test import TestCase, override_settings

from cloudflare.utils import purge_tags_from_cache, purge_all_from_cache


@override_settings(WAGTAILFRONTENDCACHE={
    'cloudflare': {
        'BACKEND': 'wagtail.contrib.wagtailfrontendcache.backends.CloudflareBackend',
        'EMAIL': 'CLOUDFLARE_FAKE_EMAIL',
        'TOKEN': 'CLOUDFLARE_FAKE_TOKEN',
        'ZONEID': 'CLOUDFLARE_FAKE_ZONE',
    }
})
class TestCacheTags(TestCase):

    @patch('cloudflare.utils.requests.delete')
    def test_cache_tag_purge(self, requests_delete):
        """
        Should fire an appropriate looking HTTP request to Cloudflare's
        purge API endpoint
        """
        purge_tags_from_cache(['tag-1', 'tag-2'])
        requests_delete.assert_called_with(
            'https://api.cloudflare.com/client/v4/zones/CLOUDFLARE_FAKE_ZONE/purge_cache',
            json={
                'tags': ['tag-1', 'tag-2']
            },
            headers={
                'X-Auth-Email': 'CLOUDFLARE_FAKE_EMAIL',
                'Content-Type': 'application/json',
                'X-Auth-Key': 'CLOUDFLARE_FAKE_TOKEN'
            }
        )

    @patch('cloudflare.utils.requests.delete')
    def test_cache_purge_all(self, requests_delete):
        """
        Should fire an appropriate looking HTTP request to Cloudflare's
        purge API endpoint
        """
        purge_all_from_cache()
        requests_delete.assert_called_with(
            'https://api.cloudflare.com/client/v4/zones/CLOUDFLARE_FAKE_ZONE/purge_cache',
            json={},
            headers={
                'X-Auth-Email': 'CLOUDFLARE_FAKE_EMAIL',
                'Content-Type': 'application/json',
                'X-Auth-Key': 'CLOUDFLARE_FAKE_TOKEN'
            }
        )
