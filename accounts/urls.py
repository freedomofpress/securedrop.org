from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from accounts.views import SecuredropList, SecuredropView, UpdateUserForm

urlpatterns = [
    url(r'accounts/instances/(?P<slug>[-\w]+)/', SecuredropView.as_view(), name='securedrop_detail'),
    url(r'accounts/instances', SecuredropList.as_view(), name='dashboard'),
    url(r'accounts/change_name/(?P<pk>[-\w]+)/', UpdateUserForm.as_view(), name='account_change_name')
]
