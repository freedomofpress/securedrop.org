import json

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import hashlib
import hmac
import logging

from github.models import Release


logger = logging.getLogger(__name__)


def validate_sha1_signature(request, secret):
    # X-Hub-Signature is the "HMAC hex digest of the payload, using the hook's
    # secret as the key."
    digest = request.META.get('HTTP_X_HUB_SIGNATURE', None)
    if not digest or digest.count('=') != 1:
        return False
    digestmod, signature = digest.split('=')
    if digestmod != 'sha1':
        logger.warn(
            'SHA1 signature validation failed due to signature of type other than sha1: %s %s',
            digestmod,
            request.META,
        )
        return False

    mac = hmac.new(secret, msg=request.body, digestmod=hashlib.sha1)
    return hmac.compare_digest(mac.hexdigest(), signature)


def handle_release_hook(release):
    try:
        release = Release(
            tag_name=release.get('tag_name', ''),
            url=release.get('html_url', ''),
            date=release.get('published_at', ''),
        )
        release.full_clean()
        release.save()
    except Exception as error:
        logger.error(
            'GitHub release event received but failed to create Release object: %s %s',
            error,
            release,
        )


@require_POST
@csrf_exempt
def receive_hook(request):
    encoding = request.encoding or settings.DEFAULT_CHARSET
    content = request.body.decode(encoding)
    if not content:
        logger.warn('GitHub hook received with no POST data')
        return HttpResponse(status=204)

    if not validate_sha1_signature(request, settings.GITHUB_HOOK_SECRET_KEY):
        logger.warn('GitHub hook received event with an invalid signature. %s', content)
        return HttpResponse(status=204)

    try:
        body = json.loads(content)
    except Exception as error:
        logger.warn('GitHub hook received erroneous JSON POST data. %s %s', content, error)
        return HttpResponse(status=204)

    event_type = request.META.get('HTTP_X_GITHUB_EVENT')
    if event_type == 'ping':
        logger.info('Ping received from GitHub hook. %s', content)
        return HttpResponse(status=204)
    elif event_type != 'release':
        logger.warn('Received an unsupported GitHub event: %s %s', event_type, content)
        return HttpResponse(status=204)

    if body.get('action', None) != 'published':
        # Currently the only `action` value for the Release hook should be
        # `published`.
        logger.warn('GitHub hook received event with an action value other than published. %s', content)
        return HttpResponse(status=204)

    release = body.get('release', False)
    if release:
        handle_release_hook(release)
    else:
        logger.warn('GitHub hook received event without a release attribute. %s', content)

    return HttpResponse(status=204)
