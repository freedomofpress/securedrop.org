from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView

from search import views as search_views
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from accounts.urls import urlpatterns as account_urls
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls
from wagtailautocomplete.views import objects, search, create
from directory.api import api_router as directory_api_router


autocomplete_public_urls = [
    url(r'^objects/', objects),
    url(r'^search/', search),
    url(r'^create/', create),
]


urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls)),
    url(r'^autocomplete/', include(autocomplete_public_urls)),
    url(r'^admin/autocomplete/', include(autocomplete_admin_urls)),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^search/$', search_views.search, name='search'),

    url(r'^github/', include('github.urls')),
    # Include the allauth and 2FA urls from their respective packages.
    url(r'^accounts/', include(account_urls)),
    url(r'^accounts/', include('allauth_2fa.urls')),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^api/$', RedirectView.as_view(url='/api/v1/')),
    url(r'^api/v1/', include(directory_api_router.urls)),

    url(r'^500/$', TemplateView.as_view(template_name="500.html")),
    url(r'^404/$', TemplateView.as_view(template_name="404.html")),
    url(r'^403/$', TemplateView.as_view(template_name="403.html")),
    url(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns

    # Debugtoolbar isnt always installed in prod, but sometimes i need to
    # toggle debug mode there.
    try:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls))
        ] + urlpatterns
    except ImportError:
        pass
