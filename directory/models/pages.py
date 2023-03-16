import dataclasses

from django.core.validators import MaxValueValidator
from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import RichTextField
from wagtail.models import Page

from common.models.mixins import MetadataPageMixin
from common.utils import paginate, DEFAULT_PAGE_KEY
from search.utils import get_search_content_by_fields
from directory.models.entry import DirectoryEntry
from directory.forms import FilterForm


@dataclasses.dataclass
class FilterDefinition:
    form_field: str
    filter_argument: str


class DirectoryPage(RoutablePageMixin, MetadataPageMixin, Page):
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    body = RichTextField(blank=True, null=True)
    source_warning = RichTextField(blank=True, null=True, help_text="A warning for sources about checking onion addresses.")
    submit_title = models.CharField(max_length=255, default="Want to get your instance listed?")
    submit_body = RichTextField(blank=True, null=True)
    submit_button_text = models.CharField(
        max_length=100,
        default="Get Started",
        help_text="Text displayed on link to scanning form.")
    manage_instances_text = models.CharField(
        max_length=100,
        default="Manage instances",
        help_text="Text displayed on link to user dashboard."
    )
    faq_link = models.ForeignKey(
        # Likely an FAQ page
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Linked to by the info icon next to 'Security' in the directory table headers."
    )
    per_page = models.PositiveSmallIntegerField(
        default=10,
        # More than 25 would be unfriendly for users.
        validators=[MaxValueValidator(25)],
        help_text='Number of news stories to display per page',
    )
    orphans = models.PositiveSmallIntegerField(
        default=2,
        validators=[MaxValueValidator(5)],
        help_text='Minimum number of stories on the last page (if the last page is smaller, they will get added to the preceding page)'
    )
    scanner_form_title = models.CharField(max_length=100, default="Scan")
    scanner_form_text = RichTextField(null=True, blank=True)
    directory_submission_form = models.ForeignKey(
        'wagtailcore.Page',
        help_text=(
            'If directory self-management tools are enabled in Directory '
            'Settings, this will have no effect. Otherwise this should be '
            'a link to a FormPage where SecureDrop admins can submit their '
            'instance to the directory'
        ),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    org_details_form_title = models.CharField(max_length=100, default="Enter organization details")
    org_details_form_text = RichTextField(null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
        MultiFieldPanel(
            heading="Sidebar",
            children=[
                FieldPanel('source_warning'),
                FieldPanel('submit_title'),
                FieldPanel('submit_body'),
                PageChooserPanel('directory_submission_form', page_type='forms.FormPage'),
                FieldPanel('submit_button_text'),
                FieldPanel('manage_instances_text'),
            ],
            classname='collapsible'
        )
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('faq_link'),
        MultiFieldPanel((
            FieldPanel('per_page'),
            FieldPanel('orphans'),
        ), 'Pagination'),
        MultiFieldPanel((
            FieldPanel('scanner_form_title'),
            FieldPanel('scanner_form_text'),
        ), 'Scanner form'),
        MultiFieldPanel((
            FieldPanel('org_details_form_title'),
            FieldPanel('org_details_form_text')
        ), 'Organization details form'),
    ]

    subpage_types = ['directory.DirectoryEntry', 'forms.FormPage']

    search_fields_pgsql = ['title', 'body', 'source_warning']

    def get_search_content(self):
        search_elements = get_search_content_by_fields(self, self.search_fields_pgsql)

        for instance in self.get_instances():
            search_elements.append(instance.title)

        return search_elements

    def get_instances(self, filters=None):
        """Get `DirectoryEntry` children of this page

        consistently filtered by visibility and `filters` parameter
        """
        instances = DirectoryEntry.objects.child_of(self).live()\
                                          .listed().order_by('title')
        if filters:
            instances = instances.filter(**filters)
        return instances

    def get_context(self, request):
        context = super(DirectoryPage, self).get_context(request)

        valid_filters = [
            FilterDefinition(
                form_field='search',
                filter_argument='title__icontains',
            ),
            FilterDefinition(form_field='language', filter_argument='languages'),
            FilterDefinition(form_field='country', filter_argument='countries'),
            FilterDefinition(form_field='topic', filter_argument='topics'),
        ]
        search_value = ''

        form = FilterForm(request.GET)
        if form.is_valid():
            entry_filters = {
                filter_def.filter_argument: form.cleaned_data[filter_def.form_field]
                for filter_def in valid_filters
                if form.cleaned_data[filter_def.form_field]
            }
            search_value = form.cleaned_data['search'].strip()
        else:
            entry_filters = {}

        entry_qs = self.get_instances(filters=entry_filters)

        paginator, entries = paginate(
            request,
            entry_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=self.per_page,
            orphans=self.orphans
        )

        context['search_value'] = search_value
        context['entries_page'] = entries
        context['entries_filters'] = entry_filters
        context['paginator'] = paginator
        context['all_filters'] = {
            'languages': form.fields['language'].queryset,
            'countries': form.fields['country'].queryset,
            'topics': form.fields['topic'].queryset,
        }

        return context
