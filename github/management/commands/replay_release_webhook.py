"""
Replay a GitHub release webhook against a running server.

Loads a fixture payload, optionally overrides repo/tag/url/date, signs it with
the server's GITHUB_HOOK_SECRET_KEY, and POSTs it to the hook endpoint.

Example:
    ./manage.py replay_release_webhook \
        --repo freedomofpress/securedrop \
        --tag 2.9.0 \
        --release-url https://github.com/freedomofpress/securedrop-inbox/releases/tag/2.9.0 \
        --published-at 2026-05-29T12:00:00Z
"""

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from urllib import request as urllib_request

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


DEFAULT_FIXTURE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "tests",
    "valid_release_hook.json",
)
DEFAULT_URL = "http://localhost:8000/github/hooks/"


class Command(BaseCommand):
    help = "Replay a GitHub release webhook against the local server."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default=DEFAULT_FIXTURE,
            help="Path to a JSON fixture to use as the payload (default: %(default)s).",
        )
        parser.add_argument(
            "--url",
            default=DEFAULT_URL,
            help="Webhook endpoint to POST to (default: %(default)s).",
        )
        parser.add_argument(
            "--repo",
            help='Override repository.full_name, e.g. "freedomofpress/securedrop".',
        )
        parser.add_argument("--tag", help="Override release.tag_name.")
        parser.add_argument("--release-url", help="Override release.html_url.")
        parser.add_argument(
            "--published-at",
            help="Override release.published_at (ISO 8601, e.g. 2024-01-15T12:00:00Z).",
        )

    def handle(self, *args, **options):
        secret = getattr(settings, "GITHUB_HOOK_SECRET_KEY", None)
        if not secret:
            raise CommandError("GITHUB_HOOK_SECRET_KEY is not set in settings.")
        if isinstance(secret, str):
            secret = secret.encode("utf-8")

        with open(options["fixture"], "r") as f:
            payload = json.load(f)

        if options.get("repo"):
            payload.setdefault("repository", {})["full_name"] = options["repo"]
        if options.get("tag"):
            payload.setdefault("release", {})["tag_name"] = options["tag"]
        if options.get("release_url"):
            payload.setdefault("release", {})["html_url"] = options["release_url"]
        elif options.get("repo") and options.get("tag"):
            payload.setdefault("release", {})["html_url"] = (
                "https://github.com/{repo}/releases/tag/{tag}".format(
                    repo=options["repo"], tag=options["tag"]
                )
            )
        if options.get("published_at"):
            payload.setdefault("release", {})["published_at"] = options["published_at"]
        elif options.get("repo") or options.get("tag"):
            payload.setdefault("release", {})["published_at"] = datetime.now(
                timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ")

        body = json.dumps(payload).encode("utf-8")
        signature = hmac.new(secret, msg=body, digestmod=hashlib.sha256).hexdigest()

        req = urllib_request.Request(
            options["url"],
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-GitHub-Event": "release",
                "X-Hub-Signature-256": "sha256={}".format(signature),
            },
            method="POST",
        )
        with urllib_request.urlopen(req) as response:
            self.stdout.write("POST {} -> {}".format(options["url"], response.status))
