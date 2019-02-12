"""
Django settings for securedrop project.

Generated by 'django-admin startproject' using Django 1.10.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

from __future__ import absolute_import, unicode_literals

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import logging
logger = logging.getLogger(__name__)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    'accounts',
    'autocomplete',
    'blog',
    'cloudflare',
    'common',
    'home',
    'marketing',
    'menus',
    'scanner',
    'search',
    'simple',
    'forms',
    'github',
    'directory',

    'wagtail.contrib.settings',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'wagtailmetadata',
    'webpack_loader',
    'taggit',
    'analytical',
    'rest_framework',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'build',

    # Configure the django-otp package.
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',

    # Enable two-factor auth.
    'allauth_2fa',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',

    # Configure the django-otp package. Note this must be after the
    # AuthenticationMiddleware.
    'django_otp.middleware.OTPMiddleware',

    # Reset login flow middleware. If this middleware is included, the login
    # flow is reset if another page is loaded between login and successfully
    # entering two-factor credentials.
    'allauth_2fa.middleware.AllauthTwoFactorMiddleware',

    # Middleware for content security policy
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'securedrop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
                'wagtail.contrib.settings.context_processors.settings'
            ],
        },
    },
]

WSGI_APPLICATION = 'securedrop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# Set the url as DATABASE_URL in the environment
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# Search Backend

if 'postgres' in DATABASES['default']['ENGINE']:
    INSTALLED_APPS.append('wagtail.contrib.postgres_search')
    WAGTAILSEARCH_BACKENDS = {
        'default': {
            'BACKEND': 'wagtail.contrib.postgres_search.backend',
        },
    }
else:
    WAGTAILSEARCH_BACKENDS = {}


# Wagtail settings

WAGTAIL_SITE_NAME = "securedrop"

WAGTAILIMAGES_IMAGE_MODEL = 'common.CustomImage'


# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'http://example.com'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Django-webpack configuration
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'bundles/',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'build/static/bundles/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}

# Sadly, we have to set these to real-looking (but invalid) values, or
# django-analytical will raise AnalyticalException. It would be preferable to be
# able to set these to None (or not be required to set them at all, which the
# django-analytical docs incorrectly suggest is possible).
PIWIK_DOMAIN_PATH = 'analytics.example.com'
# Piwik Site ID's start at 1, so 0 is an invalid ID which can be used to
# indicate to the template that the Piwik tracking code should not be rendered.
PIWIK_SITE_ID = '0'

SETTINGS_EXPORT = [
    'PIWIK_SITE_ID',
]

# django-taggit
TAGGIT_CASE_INSENSITIVE = True


# GitHub Webhook Settings

GITHUB_HOOK_SECRET_KEY = os.environ.get(
    'GITHUB_HOOK_SECRET_KEY',
    'default'
).encode('utf-8')

# django-allauth
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)
AUTH_PASSWORD_VALIDATORS = (
    {
        'NAME': 'accounts.password_validation.ZxcvbnValidator',
    },
)

WAGTAIL_FRONTEND_LOGIN_URL = '/accounts/login/'
SITE_ID = 1
LOGIN_REDIRECT_URL = "/"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_ADAPTER = 'accounts.users.adapter.MyAccountAdapter'
ACCOUNT_SIGNUP_FORM_CLASS = 'accounts.forms.SignupForm'

# Discourse API
DISCOURSE_HOST = os.environ.get('DISCOURSE_HOST', '')
DISCOURSE_API_KEY = os.environ.get('DISCOURSE_API_KEY', '')


# Logging
INSTALLED_APPS.append('django_logging')  # noqa: F405
MIDDLEWARE.append(  # noqa: F405
    'django_logging.middleware.DjangoLoggingMiddleware')
DJANGO_LOGGING = {
    "CONSOLE_LOG": False,
    "SQL_LOG": False,
    "DISABLE_EXISTING_LOGGERS": False,
    "PROPOGATE": False,
    "LOG_LEVEL": os.environ.get('DJANGO_LOG_LEVEL', 'info')
}

## Ensure base log directory exists
LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
DJANGO_OTHER_LOG = os.path.join(LOG_DIR, 'django-other.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'rotate': {
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'info').upper(),
            'class': 'logging.handlers.RotatingFileHandler',
            'backupCount': 5,
            'maxBytes': 10000000,
            'filename': os.environ.get('DJANGO_LOGFILE', DJANGO_OTHER_LOG),
            'formatter': 'django_builtin'
        },
        'null': {
            'class': 'logging.NullHandler',
        }
    },
    'formatters': {
        'django_builtin': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(module)s %(message)s'
        }
    },
    'loggers': {
        'django.template': {
            'handlers': ['rotate'],
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['rotate'],
            'propagate': False,
        },
        'django.security': {
            'handlers': ['rotate'],
            'propagate': False,
        },
        # These are already handled by the django json logging library
        'django.request': {
            'handlers': ['null'],
            'propagate': False,
        },
        '': {
            'handlers': ['rotate'],
            'propagate': False,
        },
    },
}

# Content Security Policy
# script:
# unsafe-eval for client/common/js/common.js:645 and /client/tor/js/torEntry.js:89
# All for inline scripts in wagtail (admin) login page line 44 and 92
# style:
# #1 through #8needed for inline style for svg in sliding-nav:
# #9 and #10 hashes needed for inline style for modernizr on admin page
# #11 needed for wagtail admin

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-eval'",
    # Piwik/Matomo analytics inline code:
    "'sha256-Ujy9USzNCsaDKHVACggM1NqXbQJ2ljlpMX9U4g2d5d0='",
    "analytics.freedom.press",
)
CSP_STYLE_SRC = (
    "'self'",
    "'sha256-kRJHclfjr7e5UYWHxtr0Bzdv2BiUtaSbDQe69HgEqXM='",
    "'sha256-cMOfJ1K7bmWDFQ9IoI+B6fO37u9xMiBgP1rpm79IayM='",
    "'sha256-Pf5JUUfhnnTVCCmSWFJ3qi/1j67vD2TeYvr7T6LxfqY='",
    "'sha256-aJumNcjgS5IN0N559UWLFNCtnIIo3CqO862elt0w1A0='",
    "'sha256-Rg1ua3eExI+in3cF/PWaHTHMjpiLQz/jTlIXr2kBY38='",
    "'sha256-Zbh/ZO0Ff1YEynn0zSl56u5itxZmwkCVF3PgnnOm8u4='",
    "'sha256-4ieA95gpQdpg9JDmuID1CQF8dJ/U0JnDqE4GQecAIdg='",
    "'sha256-LAw02AamnUpPKuSLFUcg9Kh2SLuqSmaXiiV45Y21f84='",
)
CSP_IMG_SRC = (
    "'self'",
    "analytics.freedom.press",
)
CSP_FRAME_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_EXCLUDE_URL_PREFIXES = ("/admin", )

# Report URI must be a string, not a tuple.
CSP_REPORT_URI = os.environ.get('DJANGO_CSP_REPORT_URI',
                                'https://freedomofpress.report-uri.com/r/d/csp/enforce')
