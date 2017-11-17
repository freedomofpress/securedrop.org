from django.views.generic import ListView, UpdateView
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from django_otp.decorators import otp_required

from accounts.forms import SecuredropPageForm
from directory.models import DirectoryPage, SCAN_URL
from landing_page_checker.models import SecuredropPage


User = get_user_model()


# Setting redirect_field_name to None will cancel redirecting, but I
# think it's necessary here to prevent that redirection from skipping
# the step where we set the 'allauth_2fa_user_id' field on the session
# (see MyAccountAdapter).
@method_decorator(otp_required(redirect_field_name=None), name='dispatch')
class SecuredropList(ListView):
    model = SecuredropPage

    def get_queryset(self, **kwargs):
        queryset = super(SecuredropList, self).get_queryset(**kwargs)
        return queryset.filter(owners__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(SecuredropList, self).get_context_data(**kwargs)
        context['create_link'] = self.get_create_link()
        return context

    def get_create_link(self):
        # This assumes that there is only one directory
        directory = DirectoryPage.objects.first()
        if directory:
            return "{}{}".format(directory.url, SCAN_URL)
        return None


@method_decorator(otp_required, name='dispatch')
class SecuredropView(UpdateView):
    template_name = 'landing_page_checker/securedroppage_form.html'
    form_class = SecuredropPageForm
    model = SecuredropPage

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user not in [owner.owner for owner in obj.owners.all()]:
            raise PermissionDenied
        return super(SecuredropView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user not in [owner.owner for owner in obj.owners.all()]:
            raise PermissionDenied
        return super(SecuredropView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.live:
            return self.object.url

        return reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super(SecuredropView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


@method_decorator(otp_required, name='dispatch')
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
