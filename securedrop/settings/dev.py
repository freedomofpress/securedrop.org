from __future__ import absolute_import, unicode_literals

import os
import socket
import struct
from django.conf import settings
from .base import *  # noqa: F403, F401

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-hf!6+rx$-55pyf6tekfkers#7cfn-_d#4f6*vnr-+vz82lqz_'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *  # noqa: F403, F401
except ImportError:
    pass


def get_default_gateway_linux():
    """
       Read the default gateway directly from /proc. Doesnt require subprocess
       or an external python dep.
       Ref: https://stackoverflow.com/questions/2761829/python-get-default-gateway-for-a-local-interface-ip-address-in-linux
    """
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


if settings.DEBUG:
    DEBUG_TOOLBAR_CONFIG = {
        'JQUERY_URL': STATIC_URL + 'debug/jquery.js',  # noqa: F405
    }

    # Obtain the default gateway from docker, needed for
    # debug toolbar whitelisting
    INTERNAL_IPS = [get_default_gateway_linux()]
    INSTALLED_APPS.append('debug_toolbar')  # noqa: F405
    INSTALLED_APPS.append('debug')  # noqa: F405
    # Needs to be injected relatively early in the MIDDLEWARE list
    MIDDLEWARE.insert(4, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405

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
