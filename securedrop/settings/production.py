from __future__ import absolute_import, unicode_literals

import os
import logging
from .base import *  # noqa: F403,F401


logger = logging.getLogger(__name__)


try:
    from .local import *  # noqa: F403,F401
except ImportError:
    pass

DEBUG = False
# SECURITY WARNING: don't run with debug turned on in production!
if os.environ.get('DJANGO_DEBUG_PROD'):
    DEBUG = True

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(' ')

# Domain specific
#
BASE_URL = os.environ.get('DJANGO_BASE_URL', 'https://securedrop.org')
STATIC_URL = os.environ.get('DJANGO_STATIC_URL', '/static/')
MEDIA_URL = os.environ.get('DJANGO_MEDIA_URL', '/media/')

# Database settings
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DJANGO_DB_NAME'],
        'USER': os.environ['DJANGO_DB_USER'],
        'PASSWORD': os.environ['DJANGO_DB_PASSWORD'],
        'HOST': os.environ['DJANGO_DB_HOST'],
        'PORT': os.environ['DJANGO_DB_PORT'],
        'CONN_MAX_AGE': os.environ.get('DJANGO_DB_MAX_AGE', 600)
    }
}

# Static and media files
#
STATIC_ROOT = os.environ['DJANGO_STATIC_ROOT']

if os.environ.get('GS_BUCKET_NAME'):
    INSTALLED_APPS.append('storages')  # noqa: F405

    GS_BUCKET_NAME = os.environ['GS_BUCKET_NAME']

    if 'GS_CUSTOM_ENDPOINT' in os.environ:
        GS_CUSTOM_ENDPOINT = os.environ['GS_CUSTOM_ENDPOINT']

    if 'GS_CREDENTIALS' in os.environ:
        from google.oauth2.service_account import Credentials
        GS_CREDENTIALS = Credentials.from_service_account_file(os.environ['GS_CREDENTIALS'])
    elif 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
        logging.warning('Defaulting to global GOOGLE_APPLICATION_CREDENTIALS')
    else:
        logging.warning(
            'GS_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS unset! ' +
            'Falling back to credentials of the machine we are running on, ' +
            'if it is a GCE instance. This is almost certainly not desired.'
        )

    GS_PROJECT_ID = os.environ.get('GS_PROJECT_ID')
    GS_MEDIA_PATH = os.environ.get('GS_MEDIA_PATH', 'media')
    GS_STATIC_PATH = os.environ.get('GS_STATIC_PATH', 'static')

    DEFAULT_FILE_STORAGE = 'common.storage.MediaStorage'
    if 'GS_STORE_STATIC' in os.environ:
        STATICFILES_STORAGE = 'common.storage.StaticStorage'
else:
    MEDIA_ROOT = os.environ['DJANGO_MEDIA_ROOT']

# Optional Elasticsearch backend - disabled by default
#
try:
    es_host = os.environ.get('DJANGO_ES_HOST', 'disable')

    if es_host == 'disable':
        WAGTAILSEARCH_BACKENDS = {}
    else:
        WAGTAILSEARCH_BACKENDS = {
            'default': {
                'BACKEND': 'wagtail.search.backends.elasticsearch2',
                'URLS': [es_host],
                'INDEX': 'wagtail',
                'TIMEOUT': 5,
                'OPTIONS': {
                    'ca_certs': os.environ['DJANGO_ES_CA_PATH'],
                    'use_ssl': True,
                }
            }
        }
except KeyError:
    pass

# Cloudflare caching
#
if os.environ.get('CLOUDFLARE_TOKEN') and os.environ.get('CLOUDFLARE_EMAIL'):
    INSTALLED_APPS.append('wagtail.contrib.frontend_cache')  # noqa: F405
    WAGTAILFRONTENDCACHE = {
        'cloudflare': {
            'BACKEND': 'wagtail.contrib.frontend_cache.backends.CloudflareBackend',
            'EMAIL': os.environ.get('CLOUDFLARE_EMAIL'),
            'TOKEN': os.environ.get('CLOUDFLARE_TOKEN'),
            'ZONEID': os.environ.get('CLOUDFLARE_ZONEID')
        },
    }

# Piwik integration for analytics
#
if os.environ.get('PIWIK_DOMAIN_PATH'):
    PIWIK_DOMAIN_PATH = os.environ.get('PIWIK_DOMAIN_PATH')
    PIWIK_SITE_ID = os.environ.get('PIWIK_SITE_ID', '5')
    # Disable auto-identify because
    # 1. we have a very small number of visitors who will be logged in and they
    #    are all FPF staff and
    # 2. auto-identify adjusts inline analytics code causing it to fail our
    #    content security policy
    ANALYTICAL_AUTO_IDENTIFY = False

# Mailgun integration
#
if os.environ.get('MAILGUN_API_KEY'):
    INSTALLED_APPS.append('anymail')  # noqa: F405
    EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
    ANYMAIL = {
        'MAILGUN_API_KEY': os.environ['MAILGUN_API_KEY'],
        'MAILGUN_SENDER_DOMAIN': os.environ['MAILGUN_SENDER_DOMAIN'],
    }
    DEFAULT_FROM_EMAIL = os.environ.get('MAILGUN_FROM_ADDR',
                                        'webmaster@mg.securedroptracker.us')

# Ensure Django knows its being served over https
SECURE_PROXY_SSL_HEADER = ('X-Forwarded-Proto', 'https')


# GitHub Webhook Settings

if GITHUB_HOOK_SECRET_KEY == b'default':  # noqa: F405
    logger.critical('GITHUB_HOOK_SECRET_KEY has a value of "default". It has likely not been set.')
