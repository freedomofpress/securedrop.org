from django.conf.urls import url

from autocomplete.views import objects, search


urlpatterns = [
    url(r'^objects/', objects),
    url(r'^search/', search),
]
