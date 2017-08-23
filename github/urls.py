from django.conf.urls import url

from github.views import receive_hook
from django.views.decorators.csrf import csrf_exempt


app_name = 'github'


urlpatterns = [
    url(r'^hooks/', receive_hook, name='receive-hook'),
]
