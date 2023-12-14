from unittest.mock import patch, Mock

from django.test import TestCase, override_settings
from requests.exceptions import HTTPError, InvalidURL

from common.tests.utils import capture_logs_with_contextvars
from cloudflare.utils import purge_tags_from_cache, purge_all_from_cache


WAGTAILFRONTENDCACHE_SETTINGS = {
    'cloudflare': {
        'BACKEND': 'wagtail.contrib.frontend_cache.backends.CloudflareBackend',
        'EMAIL': 'CLOUDFLARE_FAKE_EMAIL',
        'TOKEN': 'CLOUDFLARE_FAKE_TOKEN',
        'ZONEID': 'CLOUDFLARE_FAKE_ZONE',
    }
}


@override_settings(WAGTAILFRONTENDCACHE=WAGTAILFRONTENDCACHE_SETTINGS)
@patch('cloudflare.utils.requests.delete')
class TestCacheTags(TestCase):

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
            },
            timeout=5,
        )

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
            },
            timeout=5,
        )


@override_settings(WAGTAILFRONTENDCACHE=WAGTAILFRONTENDCACHE_SETTINGS)
@patch('cloudflare.utils.requests.delete')
class LoggingTestCase(TestCase):
    def test_log__success(self, delete_mock):
        """
        If Cloudflare's API response OK on purge, info should be logged
        """
        # Mock a successful JSON response
        delete_mock.return_value.json.return_value = {'success': True}

        with capture_logs_with_contextvars() as cap_logs:
            purge_all_from_cache()
        log_entry = cap_logs[0]
        self.assertEqual(
            log_entry,
            {
                'event': 'Purged from CloudFlare',
                'log_level': 'info',
                'cloudflare_request_data': '{}',
            },
        )

    def test_log__http_ok__cf_error(self, delete_mock):
        """
        If Clouflare's API response returns a successful HTTP response, but
        without success in the json, an error should be logged
        """
        # Mock an error JSON response
        delete_mock.return_value.json.return_value = {
            'success': False,
            'errors': [{'message': 'Cloudflare doesn\'t like you 😡'}]
        }
        with capture_logs_with_contextvars() as cap_logs:
            purge_all_from_cache()
        log_entry = cap_logs[0]
        self.assertEqual(
            log_entry,
            {
                'event': "Couldn't purge from Cloudflare.",
                'log_level': 'error',
                'cloudflare_request_data': '{}',
                'cloudflare_request_errors': 'Cloudflare doesn\'t like you 😡',
            },
        )

    def test_log__http_error(self, delete_mock):
        # Mock an HTTP error response
        response_500 = Mock()
        response_500.status_code = 500
        delete_mock.return_value.json.side_effect = ValueError
        delete_mock.return_value.raise_for_status.side_effect = HTTPError(
            'something happened',
            response=response_500
        )

        with capture_logs_with_contextvars() as cap_logs:
            purge_all_from_cache()
        log_entry = cap_logs[0]
        self.assertEqual(
            log_entry,
            {
                'event': "Couldn't purge from Cloudflare.",
                'log_level': 'error',
                'exc_info': True,
                'cloudflare_request_data': '{}',
            },
        )

    def test_log__invalid_url(self, delete_mock):
        # Mock a URL error response
        delete_mock.return_value.json.side_effect = ValueError
        delete_mock.return_value.raise_for_status.side_effect = InvalidURL(
            'something happened',
        )

        with capture_logs_with_contextvars() as cap_logs:
            purge_all_from_cache()
        log_entry = cap_logs[0]
        self.assertEqual(
            log_entry,
            {
                'event': "Couldn't purge from Cloudflare.",
                'log_level': 'error',
                'exc_info': True,
                'cloudflare_request_data': '{}',
            },
        )
