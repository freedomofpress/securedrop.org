from django.views.generic import ListView, UpdateView
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django_otp.decorators import otp_required

from common.decorators import directory_management_required
from directory.models import DirectoryPage, SCAN_URL
from landing_page_checker.models import SecuredropPage


# Setting redirect_field_name to None will cancel redirecting, but I
# think it's necessary here to prevent that redirection from skipping
# the step where we set the 'allauth_2fa_user_id' field on the session
# (see MyAccountAdapter).
@method_decorator(otp_required(redirect_field_name=None), name='dispatch')
@method_decorator(directory_management_required, name='dispatch')
class DashboardView(ListView):
    model = SecuredropPage
    template_name = 'accounts/dashboard.html'

    def get_queryset(self, **kwargs):
        queryset = super(DashboardView, self).get_queryset(**kwargs)
        return queryset.filter(owners__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['create_link'] = self.get_create_link()
        return context

    def get_create_link(self):
        # This assumes that there is only one directory
        directory = DirectoryPage.objects.first()
        if directory:
            return "{}{}".format(directory.url, SCAN_URL)
        return None


@method_decorator(otp_required, name='dispatch')
@method_decorator(directory_management_required, name='dispatch')
class UpdateUserForm(UpdateView):
    model = get_user_model()
    template_name = 'accounts/change_name.html'
    fields = ['first_name', 'last_name']
    success_url = reverse_lazy('dashboard')

    def get_object(self, **kwargs):
        obj = super(UpdateUserForm, self).get_object(**kwargs)
        if self.request.user != obj:
            raise PermissionDenied
        return obj
