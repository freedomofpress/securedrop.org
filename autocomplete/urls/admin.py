from django.conf.urls import url
from wagtail.wagtailadmin.decorators import require_admin_access

from autocomplete.views import objects, search, create


urlpatterns = [
    url(r'^objects/', require_admin_access(objects)),
    url(r'^search/', require_admin_access(search)),
    url(r'^create/', require_admin_access(create)),
]
