from datetime import datetime, timezone
import os

from django.http.request import HttpRequest
from django.test import TestCase, Client, override_settings
from django.urls import reverse
import hashlib
import hmac

from github.models import Release


class TestReceiveHook(TestCase):
    def setUp(self):
        self.client = Client()

    @override_settings(GITHUB_HOOK_SECRET_KEY=b'test')
    def test_ignore_non_release_events(self):
        json_path = os.path.join(
            os.path.dirname(__file__),
            'success_receive_hook.json',
        )
        with open(json_path, 'r') as handler:
            payload = handler.read()
            mac = hmac.new(b'test', msg=payload.encode('utf-8'), digestmod=hashlib.sha1)

        response = self.client.post(
            reverse('github:receive-hook'),
            data=payload,
            content_type='application/json',
            HTTP_X_GITHUB_EVENT='commit',
            HTTP_X_HUB_SIGNATURE='sha1={}'.format(mac.hexdigest()),
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b'test')
    def test_incorrect_signature(self):
        json_path = os.path.join(
            os.path.dirname(__file__),
            'success_receive_hook.json',
        )
        with open(json_path, 'r') as handler:
            payload = handler.read()
            mac = hmac.new(b'test', msg=(payload + 'invalid').encode('utf-8'), digestmod=hashlib.sha1)

        response = self.client.post(
            reverse('github:receive-hook'),
            data=payload,
            content_type='application/json',
            HTTP_X_GITHUB_EVENT='release',
            HTTP_X_HUB_SIGNATURE='sha1={}'.format(mac.hexdigest()),
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b'default')
    def test_incorrect_secret(self):
        json_path = os.path.join(
            os.path.dirname(__file__),
            'success_receive_hook.json',
        )
        with open(json_path, 'r') as handler:
            payload = handler.read()
            mac = hmac.new(b'test', msg=(payload).encode('utf-8'), digestmod=hashlib.sha1)

        response = self.client.post(
            reverse('github:receive-hook'),
            data=payload,
            content_type='application/json',
            HTTP_X_GITHUB_EVENT='release',
            HTTP_X_HUB_SIGNATURE='sha1={}'.format(mac.hexdigest()),
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b'test')
    def test_successful_release(self):
        json_path = os.path.join(
            os.path.dirname(__file__),
            'success_receive_hook.json',
        )
        with open(json_path, 'r') as handler:
            payload = handler.read()
            mac = hmac.new(b'test', msg=payload.encode('utf-8'), digestmod=hashlib.sha1)

        response = self.client.post(
            reverse('github:receive-hook'),
            data=payload,
            content_type='application/json',
            HTTP_X_GITHUB_EVENT='release',
            HTTP_X_HUB_SIGNATURE='sha1={}'.format(mac.hexdigest()),
        )
        release = Release.objects.last()
        self.assertEqual(release.tag_name, 'v0.1.0')
        self.assertEqual(
            release.date,
            datetime(2017, 8, 8, 21, 38, 21, tzinfo=timezone.utc)
        )
