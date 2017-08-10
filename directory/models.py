from django.db import models
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect

from modelcluster.fields import ParentalKey

from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailcore.models import Page, Orderable
from directory.utils import is_instance_valid


class DirectoryForm(forms.Form):
    instance_name = forms.CharField(label="Instance name", max_length=255)
    url = forms.URLField()
    tor_address = forms.CharField(label="Tor address", max_length=255)

    def clean(self):
        cleaned_data = super(DirectoryForm, self).clean()

        if not is_instance_valid():
            raise forms.ValidationError("Instance not valid, try again.")



class DirectoryPage(RoutablePageMixin, Page):
    @route('form/')
    def form_view(self, request):
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = DirectoryForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                # create secure_drop instance, adding parent page to the form
                return HttpResponseRedirect('{0}thanks/'.format(self.url))

        # else redirect to a page with errors
        else:
            form = DirectoryForm()

        return render(
            request,
            'directory/directory_form.html',
            {'form': form, 'submit_url': '{0}form/'.format(self.url)}
        )

    @route('thanks/')
    def thanks_view(self, request):
        return render(request, 'directory/thanks.html')


class SecureDropInstance(Orderable):
    page = ParentalKey('directory.DirectoryPage', related_name='instances')
    url = models.URLField(blank=True, null=True)
    tor_address = models.CharField(max_length=100, null=True, blank=True)
