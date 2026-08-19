import hashlib
import hmac
import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import structlog

from github.models import Product, Release

from .event_codes import EventCode


logger = structlog.get_logger()


def validate_sha256_signature(request, secret):
    # X-Hub-Signature-256 is the "HMAC hex digest of the payload, using the
    # hook's secret as the key."
    digest = request.headers.get("x-hub-signature-256", None)
    if not digest or digest.count("=") != 1:
        return False
    digestmod, signature = digest.split("=")
    if digestmod != "sha256":
        logger.warning(
            "Signature validation failed due to signature of type other than sha256",
            github_digest=digest,
            event_code=EventCode.SignatureNotSha256,
        )
        return False

    mac = hmac.new(secret, msg=request.body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)


def handle_release_hook(body):
    release_data = body["release"]
    if "rc" in release_data["tag_name"]:
        logger.info(
            "Github release event received, but ignored because release {} is "
            "release candidate".format(release_data["tag_name"])
        )
        return False
    try:
        repo_full_name = body["repository"]["full_name"]
    except KeyError:
        logger.exception(
            "GitHub release event received but missing repository information",
        )
        return False
    try:
        product = Product.objects.get(repo_full_name=repo_full_name)
    except Product.DoesNotExist:
        logger.warning(
            "Github release event received for unknown repository",
            repo_full_name=repo_full_name,
            event_code=EventCode.UnknownRepository,
        )
        return False
    try:
        release = Release(
            product=product,
            tag_name=release_data["tag_name"],
            url=release_data["html_url"],
            date=release_data["published_at"],
        )
        release.full_clean()
        release.save()
        return release
    except KeyError:
        logger.exception("GitHub release event received but failed due to missing data")
        return False
    except Exception:
        logger.exception(
            "GitHub release event received but failed to create Release object",
        )
        return False


@require_POST
@csrf_exempt
def receive_hook(request):
    encoding = request.encoding or settings.DEFAULT_CHARSET
    content = request.body.decode(encoding)
    structlog.contextvars.bind_contextvars(
        github_hook_content=content,
    )
    if not content:
        logger.warning(
            "GitHub hook received with no POST data",
            event_code=EventCode.PostDataMissing,
        )
        return HttpResponse(status=204)

    if not validate_sha256_signature(request, settings.GITHUB_HOOK_SECRET_KEY):
        logger.warning(
            "GitHub hook received event with an invalid signature.",
            event_code=EventCode.InvalidSignature,
        )
        return HttpResponse(status=204)

    try:
        body = json.loads(content)
    except Exception:
        logger.exception("GitHub hook received erroneous JSON POST data.")
        return HttpResponse(status=204)

    event_type = request.headers.get("x-github-event")
    if event_type == "ping":
        logger.info("Ping received from GitHub hook.")
        return HttpResponse(status=204)
    elif event_type != "release":
        logger.warning(
            "Received an unsupported GitHub event",
            github_event_type=event_type,
            event_code=EventCode.UnsupportedGithubEvent,
        )
        return HttpResponse(status=204)

    github_action = body.get("action", None)
    if github_action != "published":
        # Currently the only `action` value for the Release hook should be
        # `published`.
        logger.warning(
            "GitHub hook received event with an action value other than published.",
            github_action=github_action,
            event_code=EventCode.UnsupportedAction,
        )
        return HttpResponse(status=204)

    release = body.get("release", False)
    if release:
        obj = handle_release_hook(body)
        if obj:
            logger.info(
                "Successfully created release %s",
                github_release_created=obj.tag_name,
            )
    else:
        logger.warning(
            "GitHub hook received event without a release attribute.",
            event_code=EventCode.ReleaseAttributeMissing,
        )

    return HttpResponse(status=204)
