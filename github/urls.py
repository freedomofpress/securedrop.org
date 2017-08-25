from django.conf.urls import url

from github.views import receive_hook


app_name = 'github'


urlpatterns = [
    url(r'^hooks/', receive_hook, name='receive-hook'),
]
