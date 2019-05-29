import os

from django.http import HttpResponse


DEPLOYINFO_PATH = os.environ.get('DJANGO_VERSION_FILE', '/deploy/version')


def deploy_info_view(request):
    """Read deployment info file that is written by the deployment system

    This file contains git info (recent commits, messages), python
    version, dependency versions, and anything else that would be
    useful for debugging the deployed site.

    """
    try:
        with open(DEPLOYINFO_PATH, 'r') as f:
            contents = f.read()
    except FileNotFoundError:
        contents = "<file not found at {}>".format(DEPLOYINFO_PATH)
    return HttpResponse(contents, content_type='text/plain')
