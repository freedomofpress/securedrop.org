from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import url
from accounts.views import SecuredropList, SecuredropDetail, UpdateUserForm

urlpatterns = [
    url(r'accounts/instances/(?P<slug>[-\w]+)/', SecuredropDetail.as_view(), name='securedrop_detail'),
    url(r'accounts/instances', SecuredropList.as_view(), name='dashboard'),
    url(r'accounts/change_name/(?P<pk>[-\w]+)/', UpdateUserForm.as_view(), name='account_change_name')
]
