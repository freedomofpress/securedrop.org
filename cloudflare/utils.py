import logging
import requests
import json

from typing import Iterable

from wagtail.contrib.frontend_cache.utils import get_backends
from wagtail.contrib.frontend_cache.backends import CloudflareBackend


logger = logging.getLogger('wagtail.frontendcache')


def _for_every_cloudflare_backend(func: callable) -> callable:
    "Decorator to run a function once for every Cloudflare backend"

    def inner(*args, backend_settings=None, backends=None, **kwargs):
        for backend_name, backend in get_backends(backend_settings=backend_settings, backends=backends).items():
            if not isinstance(backend, CloudflareBackend):
                continue
            func(*args, backend=backend, **kwargs)

    return inner


def _purge(backend: CloudflareBackend, data={}) -> None:
    "Send a delete request to the Cloudflare API"
    purge_url = 'https://api.cloudflare.com/client/v4/zones/{0}/purge_cache'.format(backend.cloudflare_zoneid)
    string_data = json.dumps(data)

    response = requests.delete(
        purge_url,
        json=data,
        headers={
            "X-Auth-Email": backend.cloudflare_email,
            "X-Auth-Key": backend.cloudflare_token,
            "Content-Type": "application/json",
        },
    )

    try:
        try:
            response_json = response.json()
        except ValueError:
            if response.status_code != 200:
                response.raise_for_status()
            else:
                logger.error("Couldn't purge from Cloudflare with data: %s. Unexpected JSON parse error.", string_data)

    except requests.exceptions.HTTPError as e:
        logger.error("Couldn't purge from Cloudflare with data: %s. HTTPError: %d %s", string_data, e.response.status_code, str(e))
        return

    except requests.exceptions.InvalidURL as e:
        logger.error("Couldn't purge from Cloudflare with data: %s. InvalidURL: %s", string_data, str(e))
        return

    if response_json['success'] is False:
        error_messages = ', '.join([str(err['message']) for err in response_json['errors']])
        logger.error("Couldn't purge from Cloudflare with data: %s. Cloudflare errors '%s'", string_data, error_messages)
        return

    logger.info("Purged from CloudFlare with data: %s", string_data)


@_for_every_cloudflare_backend
def purge_tags_from_cache(tags: Iterable, backend: CloudflareBackend) -> None:
    "Purge tags by list. Requires an enterprise Cloudflare subscription"
    _purge(backend=backend, data={"tags": tags})


@_for_every_cloudflare_backend
def purge_all_from_cache(backend: CloudflareBackend) -> None:
    "Purge an entire zone"
    _purge(backend=backend)
