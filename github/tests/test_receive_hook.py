from datetime import datetime, timezone
import os

from django.http.request import HttpRequest
from django.test import TestCase, Client, override_settings
from django.urls import reverse
import hashlib
import hmac

from github.models import Release


class TestReceiveHook(TestCase):
    def _post_hook(self, json_file_name, secret, payload_digest_func, **kwargs):
        """
        Uses the test client to POST a release hook with the given parameters.
        Convenience method.

        Args:
            json_file_name (str): File name of JSON payload.

            secret (bytes): The key to digest the request payload with.

            payload_digest_func (function): A function which takes a payload
                and returns the message to be digested.

        Kwargs:
            github_event (str): The X-GitHub-Event header, defaults to
                "release".

            signature (str): The X-Hub-Signature header, defaults to the
                correct composition of digestmod and digest.
        """
        json_path = os.path.join(
            os.path.dirname(__file__),
            json_file_name,
        )
        with open(json_path, 'r') as handler:
            payload = handler.read()
            mac = hmac.new(
                secret,
                msg=payload_digest_func(payload).encode('utf-8'),
                digestmod=hashlib.sha1,
            )

        return self.client.post(
            reverse('github:receive-hook'),
            data=payload,
            content_type='application/json',
            HTTP_X_GITHUB_EVENT=kwargs.get('github_event', 'release'),
            HTTP_X_HUB_SIGNATURE=kwargs.get(
                'signature',
                'sha1={}'.format(mac.hexdigest())
            ),
        )

    def setUp(self):
        self.client = Client()

    @override_settings(GITHUB_HOOK_SECRET_KEY=b'test')
    def test_successful_release(self):
        response = self._post_hook(
            json_file_name='valid_release_hook.json',
            secret=b'test',
            payload_digest_func=lambda payload: payload,
        )
        release = Release.objects.last()
        self.assertEqual(release.tag_name, 'v0.1.0')
        self.assertEqual(
            release.date,
            datetime(2017, 8, 8, 21, 38, 21, tzinfo=timezone.utc)
        )

    def test_blank_request_fails(self):
        response = self.client.post(
            reverse('github:receive-hook'),
            data='',
            content_type='application/json',
            HTTP_X_GITHUB_EVENT='release',
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b'test')
    def test_ignore_non_release_events(self):
        response = self._post_hook(
            json_file_name='valid_release_hook.json',
            secret=b'test',
            payload_digest_func=lambda payload: payload,
            github_event='commit',
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b'test')
    def test_incorrect_signature_due_to_payload(self):
        response = self._post_hook(
            json_file_name='valid_release_hook.json',
            secret=b'test',
            payload_digest_func=lambda payload: payload + 'invalid',
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b'test')
    def test_incorrect_signature_format(self):
        response = self._post_hook(
            json_file_name='valid_release_hook.json',
            secret=b'test',
            payload_digest_func=lambda payload: payload,
            signature='foo',
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b'WRONG SECRET KEY')
    def test_incorrect_secret(self):
        response = self._post_hook(
            json_file_name='valid_release_hook.json',
            secret=b'test',
            payload_digest_func=lambda payload: payload,
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b'test')
    def test_missing_data_in_release_fails(self):
        response = self._post_hook(
            json_file_name='missing_key_release_hook.json',
            secret=b'test',
            payload_digest_func=lambda payload: payload,
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b'test')
    def test_non_published_action_value_ignored(self):
        response = self._post_hook(
            json_file_name='non_published_action_release_hook.json',
            secret=b'test',
            payload_digest_func=lambda payload: payload,
        )
        self.assertEqual(Release.objects.count(), 0)
