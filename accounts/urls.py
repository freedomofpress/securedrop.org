from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import url
from accounts.views import SecuredropList, SecuredropDetail

urlpatterns = [
    url(r'accounts/instances', SecuredropList.as_view()),
    url(r'accounts/something/(?P<slug>[-\w]+)/', SecuredropDetail.as_view(), name='securedrop_detail'),
]
