import os

from wagtail.documents.views import serve
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
