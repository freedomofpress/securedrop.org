from __future__ import absolute_import, unicode_literals

import os
from .base import *  # noqa: F403, F401

try:
    from .local import *  # noqa: F403, F401
except ImportError:
    pass

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(' ')

# Domain specific
#
BASE_URL = os.environ.get('DJANGO_BASE_URL', 'https://freedom.press')
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
                'BACKEND': 'wagtail.wagtailsearch.backends.elasticsearch2',
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

# Django logging
#   django-json logging needs some work, but its off by default so lets
#   leave it in for now
if os.environ.get('DJANGO_JSON_LOG', 'no').lower() in ['true', 'yes']:
    INSTALLED_APPS.append('django_logging')  # noqa: F405
    MIDDLEWARE.append(  # noqa: F405
        'django_logging.middleware.DjangoLoggingMiddleware')
    DJANGO_LOGGING = {
        "CONSOLE_LOG": False,
        "SQL_LOG": False,
        "DISABLE_EXISTING_LOGGERS": True,
        "LOG_LEVEL": os.environ.get('DJANGO_LOG_LEVEL', 'info')
    }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'rotate': {
                'level': os.environ.get('DJANGO_LOG_LEVEL', 'info').upper(),
                'class': 'logging.handlers.RotatingFileHandler',
                'backupCount': 5,
                'maxBytes': 10000000,
                'filename': os.environ.get('DJANGO_LOGFILE',
                                           '/var/log/securedrop/django.log')
            },
        },
        'loggers': {
            '': {
                'handlers': ['rotate'],
                'level': os.environ.get('DJANGO_LOG_LEVEL', 'info').upper(),
                'propagate': True,
            },
        },
    }

# Cloudflare caching
#
if os.environ.get('CLOUDFLARE_TOKEN') and os.environ.get('CLOUDFLARE_EMAIL'):
    INSTALLED_APPS.append('wagtail.contrib.wagtailfrontendcache')  # noqa: F405
    WAGTAILFRONTENDCACHE = {
        'cloudflare': {
            'BACKEND': 'wagtail.contrib.wagtailfrontendcache.backends.CloudflareBackend',
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
