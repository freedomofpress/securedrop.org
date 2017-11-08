from unittest import mock

import requests
from django.test import TestCase

from search.utils.discourse.client import DiscourseClient


class DiscourseClientTestCase(TestCase):
    def setUp(self):
        self.client = DiscourseClient('example.com', 'fake_api_key')

    @mock.patch('search.utils.discourse.client.requests.request')
    def test_successful_get(self, mock_get):
        """Discourse client should execute get requests successfully"""
        mock_response = mock.Mock()

        expected = {
            'post_stream': 'stream',
            'id': 0,
        }
        mock_response.json.return_value = expected
        mock_get.return_value = mock_response

        path = '/test/'
        data = {'item': 1}
        response = self.client._get(path, data)

        mock_get.assert_called_once_with(
            'GET',
            'https://example.com/test/',
            data={'item': 1, 'api_key': 'fake_api_key'},
        )
        self.assertEqual(mock_response.json.call_count, 1)
        self.assertEqual(expected, response)

    @mock.patch('search.utils.discourse.client.logger')
    @mock.patch('search.utils.discourse.client.requests.request')
    def test_get_with_exception(self, mock_get, mock_logger):
        """Discourse client should handle HTTP exceptions and return False"""
        mock_response = mock.Mock()
        mock_error = mock.Mock()
        http_error = requests.exceptions.HTTPError()
        mock_response.raise_for_status.side_effect = http_error
        mock_logger.error = mock_error

        mock_get.return_value = mock_response

        path = '/test/'
        data = {'item': 1}
        response = self.client._get(path, data)

        mock_error.assert_called_once_with(
            'Error making %r request to Discourse URL %r: %s',
            'GET',
            'https://example.com/test/',
            http_error,
        )
        self.assertIs(response, False)

    @mock.patch('search.utils.discourse.client.logger')
    @mock.patch('search.utils.discourse.client.requests.request')
    def test_get_connection_error(self, mock_get, mock_logger):
        """Discourse client should handle persistent connection failures"""
        mock_response = mock.Mock()
        mock_error = mock.Mock()
        connection_error = requests.exceptions.ConnectionError()
        mock_response.raise_for_status.side_effect = connection_error
        mock_logger.error = mock_error

        mock_get.return_value = mock_response

        path = '/test/'
        data = {'item': 1}
        response = self.client._get(path, data)

        method = 'GET'
        url = 'https://example.com/test/'
        final_data = {'item': 1, 'api_key': 'fake_api_key'}
        expected_calls = [mock.call(method, url, data=final_data)] * 3

        self.assertEqual(expected_calls, mock_get.call_args_list)
        mock_error.assert_called_once_with(
            'Connection failed on %r request to Discourse URL %r: %s',
            'GET',
            'https://example.com/test/',
            connection_error,
        )
        self.assertIs(response, False)
