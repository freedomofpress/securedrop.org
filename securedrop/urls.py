from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.urls import path, re_path, include
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
    path('objects/', objects),
    path('search/', search),
    path('create/', create),
]


urlpatterns = [
    path('django-admin/', admin.site.urls),
    re_path(r'^autocomplete/', include(autocomplete_public_urls)),
    re_path(r'^admin/autocomplete/', include(autocomplete_admin_urls)),
    re_path(r'^admin/', include(wagtailadmin_urls)),
    re_path(r'^documents/', include(wagtaildocs_urls)),

    re_path(r'^search/$', search_views.search, name='search'),

    re_path(r'^github/', include('github.urls')),
    # Include the allauth and 2FA urls from their respective packages.
    re_path(r'^accounts/', include(account_urls)),
    re_path(r'^accounts/', include('allauth_2fa.urls')),
    re_path(r'^accounts/', include('allauth.urls')),

    re_path(r'^api/$', RedirectView.as_view(url='/api/v1/')),
    re_path(r'^api/v1/', include(directory_api_router.urls)),

    re_path(r'^500/$', TemplateView.as_view(template_name="500.html")),
    re_path(r'^404/$', TemplateView.as_view(template_name="404.html")),
    re_path(r'^403/$', TemplateView.as_view(template_name="403.html")),
    re_path(r'', include(wagtail_urls)),
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
            re_path(r'^__debug__/', include(debug_toolbar.urls))
        ] + urlpatterns
    except ImportError:
        pass
