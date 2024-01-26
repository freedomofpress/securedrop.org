from wagtail import hooks
from django.urls import re_path

from .views import deploy_info_view


@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        re_path(r'^version/?$', deploy_info_view, name='deployinfo'),
    ]
