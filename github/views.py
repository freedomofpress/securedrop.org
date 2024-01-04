import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import hashlib
import hmac
import structlog

from github.models import Release

from .event_codes import EventCode


logger = structlog.get_logger()


def validate_sha1_signature(request, secret):
    # X-Hub-Signature is the "HMAC hex digest of the payload, using the hook's
    # secret as the key."
    digest = request.META.get('HTTP_X_HUB_SIGNATURE', None)
    if not digest or digest.count('=') != 1:
        return False
    digestmod, signature = digest.split('=')
    if digestmod != 'sha1':
        logger.warn(
            'SHA1 signature validation failed due to signature of type other than sha1',
            github_digest=digest,
            event_code=EventCode.SignatureNotSha1,
        )
        return False

    mac = hmac.new(secret, msg=request.body, digestmod=hashlib.sha1)
    return hmac.compare_digest(mac.hexdigest(), signature)


def handle_release_hook(release):
    if 'rc' in release['tag_name']:
        logger.info(
            'Github release event received, but ignored because release {} is '
            'release candidate'.format(release['tag_name'])
        )
        return False
    try:
        release = Release(
            tag_name=release['tag_name'],
            url=release['html_url'],
            date=release['published_at'],
        )
        release.full_clean()
        release.save()
        return release
    except KeyError:
        logger.exception(
            'GitHub release event received but failed due to missing data'
        )
        return False
    except Exception:
        logger.exception(
            'GitHub release event received but failed to create Release object',
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
        logger.warn(
            'GitHub hook received with no POST data',
            event_code=EventCode.PostDataMissing,
        )
        return HttpResponse(status=204)

    if not validate_sha1_signature(request, settings.GITHUB_HOOK_SECRET_KEY):
        logger.warn(
            'GitHub hook received event with an invalid signature.',
            event_code=EventCode.InvalidSignature,
        )
        return HttpResponse(status=204)

    try:
        body = json.loads(content)
    except Exception:
        logger.exception('GitHub hook received erroneous JSON POST data.')
        return HttpResponse(status=204)

    event_type = request.META.get('HTTP_X_GITHUB_EVENT')
    if event_type == 'ping':
        logger.info('Ping received from GitHub hook.')
        return HttpResponse(status=204)
    elif event_type != 'release':
        logger.warn(
            'Received an unsupported GitHub event',
            github_event_type=event_type,
            event_code=EventCode.UnsupportedGithubEvent,
        )
        return HttpResponse(status=204)

    github_action = body.get('action', None)
    if github_action != 'published':
        # Currently the only `action` value for the Release hook should be
        # `published`.
        logger.warn(
            'GitHub hook received event with an action value other than published.',
            github_action=github_action,
            event_code=EventCode.UnsupportedAction,
        )
        return HttpResponse(status=204)

    release = body.get('release', False)
    if release:
        obj = handle_release_hook(release)
        if obj:
            logger.info(
                'Successfully created release %s',
                github_release_created=obj.tag_name,
            )
    else:
        logger.warn(
            'GitHub hook received event without a release attribute.',
            event_code=EventCode.ReleaseAttributeMissing,
        )

    return HttpResponse(status=204)
