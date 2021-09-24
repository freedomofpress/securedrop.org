import os

from wagtail.documents.views import serve
from django.http import HttpResponse
from django.views.decorators.cache import never_cache


VERSION_INFO_SHORT_PATH = os.environ.get(
    "DJANGO_SHORT_VERSION_FILE", "/deploy/version-short.txt"
)
VERSION_INFO_FULL_PATH = os.environ.get(
    "DJANGO_FULL_VERSION_FILE", "/deploy/version-full.txt"
)


def read_version_info_file(p):
    """Read deployment info file that is written by the deployment system

    This file contains git info (recent commits, messages), python
    version, dependency versions, and anything else that would be
    useful for debugging the deployed site.

    """
    try:
        with open(p, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "<file not found at {}>".format(p)


def deploy_info_view(request):
    version_full_text = read_version_info_file(VERSION_INFO_FULL_PATH)
    return HttpResponse(version_full_text, content_type="text/plain")


def view_document(request, document_id, document_filename):
    """
    Calls the normal document `serve` view, except makes it not an attachment.
    """
    # Get response from `serve` first
    response = serve.serve(request, document_id, document_filename)

    # Remove "attachment" from response's Content-Disposition
    if 'Content-Disposition' in response:
        contdisp = response['Content-Disposition']
        response['Content-Disposition'] = "; ".join(
            [x for x in contdisp.split("; ") if x != "attachment"]
        )

    # Force content-type for pdf files
    if document_filename.split('.')[-1] == 'pdf':
        response['Content-Type'] = 'application/pdf'

    # Return the response
    return response


@never_cache
def health_ok(request):
    """Lightweight health-check with a 200 response code."""
    return HttpResponse("okay", content_type="text/plain")

def health_version(request):
    """Also a health check, but returns the commit short-hash."""
    version_short_text = read_version_info_file(VERSION_INFO_SHORT_PATH)
    return HttpResponse(version_short_text, content_type="text/plain")
