import hashlib
import hmac
import os
from datetime import datetime, timezone
from unittest import mock

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from github.models import Product, Release


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
        with open(json_path, "r") as handler:
            payload = handler.read()
            mac = hmac.new(
                secret,
                msg=payload_digest_func(payload).encode("utf-8"),
                digestmod=hashlib.sha1,
            )

        return self.client.post(
            reverse("github:receive-hook"),
            data=payload,
            content_type="application/json",
            headers={
                "x-github-event": kwargs.get("github_event", "release"),
                "x-hub-signature": kwargs.get(
                    "signature", "sha1={}".format(mac.hexdigest())
                ),
            },
        )

    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Hook Test",
            slug="hook-test",
            repo_full_name="notfreedomofpress/hook-test",
        )

    @override_settings(GITHUB_HOOK_SECRET_KEY=b"test")
    def test_successful_release(self):
        self._post_hook(
            json_file_name="valid_release_hook.json",
            secret=b"test",
            payload_digest_func=lambda payload: payload,
        )
        release = Release.objects.last()
        self.assertEqual(release.tag_name, "v0.1.0")
        self.assertEqual(
            release.date, datetime(2017, 8, 8, 21, 38, 21, tzinfo=timezone.utc)
        )
        self.assertEqual(release.product, self.product)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b"test")
    def test_unknown_repository_ignored(self):
        """
        A release from a repository with no matching Product should be dropped
        and not create a Release.
        """
        self.product.delete()
        self._post_hook(
            json_file_name="valid_release_hook.json",
            secret=b"test",
            payload_digest_func=lambda payload: payload,
        )
        self.assertEqual(Release.objects.count(), 0)

    @mock.patch("github.views.logger")
    @override_settings(GITHUB_HOOK_SECRET_KEY=b"test")
    def test_release_candidate(self, mock_logger):
        """
        A release with a `-rc` tag name should not trigger a new Release object
        to be created
        """
        mock_logger.info = mock.Mock()

        self._post_hook(
            json_file_name="valid_release_hook__candidate.json",
            secret=b"test",
            payload_digest_func=lambda payload: payload,
        )

        self.assertFalse(Release.objects.all().exists())
        mock_logger.info.assert_any_call(
            "Github release event received, but ignored because release "
            "0.6-rc2 is release candidate"
        )

    def test_blank_request_fails(self):
        self.client.post(
            reverse("github:receive-hook"),
            data="",
            content_type="application/json",
            headers={"x-github-event": "release"},
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b"test")
    def test_ignore_non_release_events(self):
        self._post_hook(
            json_file_name="valid_release_hook.json",
            secret=b"test",
            payload_digest_func=lambda payload: payload,
            github_event="commit",
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b"test")
    def test_incorrect_signature_due_to_payload(self):
        self._post_hook(
            json_file_name="valid_release_hook.json",
            secret=b"test",
            payload_digest_func=lambda payload: payload + "invalid",
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b"test")
    def test_incorrect_signature_format(self):
        self._post_hook(
            json_file_name="valid_release_hook.json",
            secret=b"test",
            payload_digest_func=lambda payload: payload,
            signature="foo",
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b"test")
    def test_incorrect_signature_type(self):
        self._post_hook(
            json_file_name="valid_release_hook.json",
            secret=b"test",
            payload_digest_func=lambda payload: payload,
            signature="md5=39382",
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b"WRONG SECRET KEY")
    def test_incorrect_secret(self):
        self._post_hook(
            json_file_name="valid_release_hook.json",
            secret=b"test",
            payload_digest_func=lambda payload: payload,
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b"test")
    def test_missing_data_in_release_fails(self):
        self._post_hook(
            json_file_name="missing_key_release_hook.json",
            secret=b"test",
            payload_digest_func=lambda payload: payload,
        )
        self.assertEqual(Release.objects.count(), 0)

    @override_settings(GITHUB_HOOK_SECRET_KEY=b"test")
    def test_non_published_action_value_ignored(self):
        self._post_hook(
            json_file_name="non_published_action_release_hook.json",
            secret=b"test",
            payload_digest_func=lambda payload: payload,
        )
        self.assertEqual(Release.objects.count(), 0)
