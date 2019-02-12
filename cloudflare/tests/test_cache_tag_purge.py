from unittest.mock import patch, Mock

from django.test import TestCase, override_settings
from requests.exceptions import HTTPError, InvalidURL

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
            }
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
            }
        )


@override_settings(WAGTAILFRONTENDCACHE=WAGTAILFRONTENDCACHE_SETTINGS)
@patch('cloudflare.utils.requests.delete')
@patch('cloudflare.utils.logger')
class LoggingTestCase(TestCase):
    def test_log__success(self, logger_mock, delete_mock):
        """
        If Cloudflare's API response OK on purge, info should be logged
        """
        # Mock a successful JSON response
        delete_mock.return_value.json.return_value = {'success': True}
        purge_all_from_cache()
        logger_mock.info.assert_called_once_with(
            'Purged from CloudFlare with data: %s',
            '{}'
        )

    def test_log__http_ok__cf_error(self, logger_mock, delete_mock):
        """
        If Clouflare's API response returns a successful HTTP response, but
        without success in the json, an error should be logged
        """
        # Mock an error JSON response
        delete_mock.return_value.json.return_value = {
            'success': False,
            'errors': [{'message': 'Cloudflare doesn\'t like you 😡'}]
        }
        purge_all_from_cache()
        logger_mock.error.assert_called_once_with(
            'Couldn\'t purge from Cloudflare with data: %s. '
            'Cloudflare errors \'%s\'',
            '{}',
            'Cloudflare doesn\'t like you 😡'
        )

    def test_log__http_error(self, logger_mock, delete_mock):
        # Mock an HTTP error response
        response_500 = Mock()
        response_500.status_code = 500
        delete_mock.return_value.json.side_effect = ValueError
        delete_mock.return_value.raise_for_status.side_effect = HTTPError(
            'something happened',
            response=response_500
        )

        purge_all_from_cache()
        logger_mock.error.assert_called_once_with(
            'Couldn\'t purge from Cloudflare with data: %s. HTTPError: %d %s',
            '{}',
            500,
            'something happened'
        )

    def test_log__invalid_url(self, logger_mock, delete_mock):
        # Mock a URL error response
        delete_mock.return_value.json.side_effect = ValueError
        delete_mock.return_value.raise_for_status.side_effect = InvalidURL(
            'something happened',
        )

        purge_all_from_cache()
        logger_mock.error.assert_called_once_with(
            'Couldn\'t purge from Cloudflare with data: %s. InvalidURL: %s',
            '{}',
            'something happened'
        )
