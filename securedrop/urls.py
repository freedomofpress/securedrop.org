from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.urls import re_path, path, include
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView

from search import views as search_views
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

import common.views as common_views
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
    path('autocomplete/', include(autocomplete_public_urls)),
    path('admin/autocomplete/', include(autocomplete_admin_urls)),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    re_path(
        r'^document/view/(\d+)/(.*)$',
        common_views.view_document,
        name='view_document'
    ),
    path('health/ok/', common_views.health_ok),
    path('health/version/', common_views.health_version),
    path('sitemap.xml', sitemap, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

    path('search/', search_views.search, name='search'),

    path('github/', include('github.urls')),

    path('api/', RedirectView.as_view(url='/api/v1/')),
    path('api/v1/', include(directory_api_router.urls)),

    path('500/', TemplateView.as_view(template_name="500.html")),
    path('404/', TemplateView.as_view(template_name="404.html")),
    path('403/', TemplateView.as_view(template_name="403.html")),
    path('429/', common_views.too_many_requests, name='too_many_requests'),
    path(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns

    if settings.ENABLE_DEBUG_TOOLBAR:
        from debug_toolbar.toolbar import debug_toolbar_urls

        urlpatterns += debug_toolbar_urls()
