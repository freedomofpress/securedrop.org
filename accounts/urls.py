from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from accounts.views import DashboardView, UpdateUserForm
from landing_page_checker.views import SecuredropEditView

urlpatterns = [
    url(r'^dashboard$', DashboardView.as_view(), name='dashboard'),
    url(r'^change_name/(?P<pk>[-\w]+)/', UpdateUserForm.as_view(), name='account_change_name'),
    url(r'^instances/add/$', SecuredropEditView.as_view(), name='securedroppage_add'),
    url(r'^instances/(?P<pk>[0-9]+)/$', SecuredropEditView.as_view(), name='securedroppage_edit'),
]
