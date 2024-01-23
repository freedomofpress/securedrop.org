from django.urls import path

from github.views import receive_hook


app_name = 'github'


urlpatterns = [
    path('hooks/', receive_hook, name='receive-hook'),
]
