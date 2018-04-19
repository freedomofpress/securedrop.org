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

    @mock.patch('search.utils.discourse.client.requests.request')
    def test_get_with_exception(self, mock_get):
        """Discourse client should raise up HTTP exceptions"""
        mock_response = mock.Mock()
        http_error = requests.exceptions.HTTPError()
        mock_response.raise_for_status.side_effect = http_error

        mock_get.return_value = mock_response

        path = '/test/'
        data = {'item': 1}

        with self.assertRaises(requests.exceptions.HTTPError):
            self.client._get(path, data)

    @mock.patch('search.utils.discourse.client.requests.request')
    def test_get_connection_error(self, mock_get):
        """Discourse client should raise up persistent connection failures"""
        mock_response = mock.Mock()
        connection_error = requests.exceptions.ConnectionError()
        mock_response.raise_for_status.side_effect = connection_error

        mock_get.return_value = mock_response

        path = '/test/'
        data = {'item': 1}

        # We expect it to raise an error
        with self.assertRaises(requests.exceptions.ConnectionError):
            self.client._get(path, data)

        # We also expect it to have attempted to call `request` three times
        # before raising an error
        method = 'GET'
        url = 'https://example.com/test/'
        final_data = {'item': 1, 'api_key': 'fake_api_key'}
        expected_calls = [mock.call(method, url, data=final_data)] * 3
        self.assertEqual(expected_calls, mock_get.call_args_list)

    @mock.patch('search.utils.discourse.client.requests.request')
    def test_get_connection_error_then_success(self, mock_get):
        mock_response = mock.Mock()
        expected = {
            'post_stream': 'stream',
            'id': 0,
        }
        mock_response.json.return_value = expected
        connection_error = requests.exceptions.ConnectionError()

        mock_get.side_effect = [connection_error, connection_error, mock_response]

        path = '/test/'
        data = {'item': 1}
        response = self.client._get(path, data)

        method = 'GET'
        url = 'https://example.com/test/'
        final_data = {'item': 1, 'api_key': 'fake_api_key'}
        expected_calls = [mock.call(method, url, data=final_data)] * 3

        self.assertEqual(expected_calls, mock_get.call_args_list)

        self.assertEqual(mock_response.json.call_count, 1)
        self.assertEqual(expected, response)

    @mock.patch('time.sleep')
    @mock.patch('search.utils.discourse.client.requests.request')
    def test_get_sleep_and_retry(self, mock_get, mock_sleep):
        """
        Discouse client should sleep if it receives a response 429 and then
        retry
        """

        # Mock a normal response
        mock_response = mock.Mock()
        expected = {
            'post_stream': 'stream',
            'id': 0,
        }
        mock_response.json.return_value = expected

        # Mock an error code 429 response
        response_429 = requests.Response()
        response_429.status_code = 429
        http_429_error = requests.exceptions.HTTPError(response=response_429)

        mock_get.side_effect = [http_429_error, mock_response]

        # Trigger the request
        path = '/test/'
        data = {'item': 1}
        response = self.client._get(path, data)

        mock_sleep.assert_called_once_with(30)
        self.assertEqual(mock_response.json.call_count, 1)
        self.assertEqual(expected, response)
