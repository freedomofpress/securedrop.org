from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, UpdateView
from django_otp.decorators import otp_required
from wagtail.core.models import Site

from directory.decorators import directory_management_required
from directory.models.settings import DirectorySettings
from directory.models import DirectoryPage, DirectoryEntry
from accounts.forms import DirectoryEntryOwnerForm


class SecuredropListView(ListView):
    model = DirectoryEntry
    template_name = 'home.html'


class SecuredropDetailView(DetailView):
    model = DirectoryEntry
    template_name = 'securedrop_detail.html'


@method_decorator(directory_management_required, name='dispatch')
@method_decorator(otp_required(redirect_field_name=None), name='dispatch')
class SecuredropEditView(UpdateView):
    template_name = 'directory_management/securedroppage_form.html'
    form_class = DirectoryEntryOwnerForm
    model = DirectoryEntry

    def get_object(self):
        self.directory_page = DirectoryPage.objects.first()

        if 'slug' in self.kwargs:
            obj = super(SecuredropEditView, self).get_object()

            if not obj.owners.filter(owner=self.request.user).exists():
                raise PermissionDenied

            return obj
        return None

    def get_success_url(self):
        return reverse('dashboard')

    def get_form_kwargs(self):
        kwargs = super(SecuredropEditView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'directory_page': self.directory_page,
        })
        return kwargs

    def form_valid(self, form):
        response = super(SecuredropEditView, self).form_valid(form)
        site = Site.find_for_request(self.request)
        directory_settings = DirectorySettings.for_site(site)
        if directory_settings.new_instance_alert_group:
            recipient_emails = directory_settings.new_instance_alert_group.user_set.values_list('email', flat=True)
            send_mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_emails,
                subject='New Securedrop instance on directory',
                message='A new Securedrop instance was added to {}. Moderate and approve here: {}{}'.format(
                    site.site_name,
                    site.root_url,
                    reverse('wagtailadmin_pages:edit', args=(self.object.pk,)),
                ),
            )

        return response

    def form_invalid(self, form):
        # Delete the created logo if this is a failed creation
        organization_logo = form.cleaned_data.get('organization_logo')
        if self.object is None and organization_logo:
            organization_logo.delete()
        return super(SecuredropEditView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(SecuredropEditView, self).get_context_data(**kwargs)
        context.update({
            'form_title': self.directory_page.org_details_form_title,
            'text': self.directory_page.org_details_form_text,
        })
        return context
