from landing_page_checker.models import SecuredropPage
from django.views.generic import ListView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from accounts.forms import SecuredropPageForm

User = get_user_model()


@method_decorator(login_required, name='dispatch')
class SecuredropList(ListView):
    model = SecuredropPage

    def get_queryset(self, **kwargs):
        queryset = super(SecuredropList, self).get_queryset(**kwargs)
        return queryset.filter(owners__owner=self.request.user)


@method_decorator(login_required, name='dispatch')
class SecuredropView(UpdateView):
    template_name = 'landing_page_checker/securedroppage_form.html'
    form_class = SecuredropPageForm
    model = SecuredropPage
    error_css_class = 'basic-form__error'
    required_css_class = 'basic-form__required'

    def get_success_url(self):
        if self.object.live:
            return self.object.url

        return reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super(SecuredropView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


@method_decorator(login_required, name='dispatch')
class UpdateUserForm(UpdateView):
    model = get_user_model()
    template_name = 'accounts/change_name.html'
    fields = ['first_name', 'last_name']
    success_url = reverse_lazy('dashboard')
    error_css_class = 'basic-form__error'
    required_css_class = 'basic-form__required'

    def get_object(self, **kwargs):
        obj = super(UpdateUserForm, self).get_object(**kwargs)
        if self.request.user != obj:
            raise PermissionDenied
        return obj
