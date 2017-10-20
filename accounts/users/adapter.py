from django.conf import settings
from django.urls import reverse
from allauth.account.adapter import DefaultAccountAdapter


class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        path = reverse('securedrop_list')
        return path
