from django.conf.urls import url

from autocomplete.views import objects, search, create


urlpatterns = [
    url(r'^objects/', objects),
    url(r'^search/', search),
    url(r'^create/', create),
]
