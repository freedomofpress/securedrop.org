from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.text import slugify

from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import (
    InlinePanel,
)

from landing_page_checker.landing_page import scanner
from landing_page_checker.models import Securedrop


class DirectoryForm(forms.Form):
    instance_name = forms.CharField(label="Instance name", max_length=255)
    organization = forms.CharField(label="Organization", max_length=255)
    url = forms.URLField()
    tor_address = forms.CharField(label="Tor address", max_length=255)


class DirectoryPage(RoutablePageMixin, Page):
    @route('form/')
    def form_view(self, request):
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = DirectoryForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                data = form.cleaned_data
                # create secure_drop instance, adding parent page to the form
                instance = Securedrop.objects.create(
                    page=self,
                    landing_page_domain=data['url'],
                    organization=data['organization'],
                    slug=slugify(data['organization']),
                    onion_address=data['tor_address'],
                )
                result = scanner.scan(instance)
                result.save()

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

    content_panels = Page.content_panels + [
        InlinePanel('instances', label='Thingies'),
    ]
