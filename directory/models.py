from django.db import models
from django.shortcuts import render
from django.http import HttpResponseRedirect

from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page

from common.models.mixins import MetadataPageMixin
from directory.forms import DirectoryForm
from landing_page_checker.landing_page import scanner
from landing_page_checker.models import SecuredropPage as SecuredropInstance


class DirectoryPage(RoutablePageMixin, MetadataPageMixin, Page):
    body = RichTextField(blank=True, null=True)
    source_warning = RichTextField(blank=True, null=True, help_text="A warning for sources about checking onion addresses.")
    submit_title = models.CharField(max_length=255, default="Want to get your instance listed?")
    submit_body = RichTextField(blank=True, null=True)
    submit_button_text = models.CharField(
        max_length=100,
        default="Scan my instance",
        help_text="Text displayed on link to scanning form.")

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        MultiFieldPanel(
            heading="Sidebar",
            children=[
                FieldPanel('source_warning'),
                FieldPanel('submit_title'),
                FieldPanel('submit_body'),
                FieldPanel('submit_button_text')
            ],
            classname='collapsible'
        )
    ]

    subpage_types = ['landing_page_checker.SecuredropPage']

    @route('form/')
    def form_view(self, request):
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            form = DirectoryForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                data = form.cleaned_data
                # create secure_drop instance, adding parent page to the form
                instance = SecuredropInstance(
                    title=data['organization'],
                    landing_page_domain=data['url'],
                    organization=data['organization'],
                    onion_address=data['tor_address'],
                )
                self.add_child(instance=instance)
                instance.save()
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
