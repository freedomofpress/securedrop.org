from django.http import Http404
from wagtail.core.models import Site

from directory.models.settings import DirectorySettings


def directory_management_required(func):
    """
    Decorator that alters a function to raise Http404 if directory management
    is not allowed by DirectorySettings
    """

    def inner(request, *args, **kwargs):
        directory_settings = DirectorySettings.for_site(Site.find_for_request(request))
        if not directory_settings.allow_directory_management:
            raise Http404
        return func(request, *args, **kwargs)

    return inner
