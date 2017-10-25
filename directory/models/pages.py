from django.core.validators import MaxValueValidator
from django.db import models
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page

from common.models.mixins import MetadataPageMixin
from common.utils import paginate, DEFAULT_PAGE_KEY, get_search_content_by_fields
from directory.models import Language, Topic, Country
from directory.forms import DirectoryForm, ScannerForm
from landing_page_checker.landing_page import scanner
from landing_page_checker.models import SecuredropPage as SecuredropInstance


SCAN_URL = 'scan/'


class DirectoryPage(RoutablePageMixin, MetadataPageMixin, Page):
    body = RichTextField(blank=True, null=True)
    source_warning = RichTextField(blank=True, null=True, help_text="A warning for sources about checking onion addresses.")
    submit_title = models.CharField(max_length=255, default="Want to get your instance listed?")
    submit_body = RichTextField(blank=True, null=True)
    submit_button_text = models.CharField(
        max_length=100,
        default="Get Started",
        help_text="Text displayed on link to scanning form.")
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
    org_details_form_title = models.CharField(max_length=100, default="Enter organization details")
    org_details_form_text = RichTextField(null=True, blank=True)
    thank_you_title = models.CharField(max_length=100, default="Thank you")
    thank_you_text = RichTextField(null=True, blank=True)

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

    settings_panels = Page.settings_panels + [
        PageChooserPanel('faq_link'),
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
        MultiFieldPanel((
            FieldPanel('thank_you_title'),
            FieldPanel('thank_you_text')
        ), 'Successful form submit text'),

    ]

    subpage_types = ['landing_page_checker.SecuredropPage']

    search_fields_pgsql = ['title', 'body', 'source_warning']

    def get_search_content(self):
        search_content = get_search_content_by_fields(self, self.search_fields_pgsql)

        for instance in self.get_instances():
            search_content += instance.title + ' '

        return search_content

    def get_instances(self, filters=None):
        """Get `SecuredropPage` children of this page

        consistently filtered by visibility and `filters` parameter
        """
        instances = SecuredropInstance.objects.child_of(self).live()
        if filters:
            instances = instances.filter(**filters)
        return instances

    def filters_from_querydict(self, query):
        """Accept a querydict and return a list of queryset filters

        Currently accepts the following get keys:
        - `language` an language id
        - `country` a country id
        - `topic` a topic id

        Returns filters with objects, not PKs because objects can be used
        to render information about the filter in the template. (I.e., "You
        are filtering for instances that list Spanish as a language")
        Returns an empty filters object if PKs are invalid.
        """
        filters = {}
        language_id = query.get('language')
        country_id = query.get('country')
        topic_id = query.get('topic')
        if language_id:
            try:
                filters['languages'] = Language.objects.get(id=language_id)
            except ValueError:
                pass
            except Language.DoesNotExist:
                pass

        if country_id:
            try:
                filters['countries'] = Country.objects.get(id=country_id)
            except ValueError:
                pass
            except Country.DoesNotExist:
                pass

        if topic_id:
            try:
                filters['topics'] = Topic.objects.get(id=topic_id)
            except ValueError:
                pass
            except Country.DoesNotExist:
                pass

        return filters

    def get_context(self, request):
        context = super(DirectoryPage, self).get_context(request)

        entry_filters = self.filters_from_querydict(request.GET)
        entry_qs = self.get_instances(filters=entry_filters)

        paginator, entries = paginate(
            request,
            entry_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=self.per_page,
            orphans=self.orphans
        )

        context['entries_page'] = entries
        context['entries_filters'] = entry_filters
        context['paginator'] = paginator
        context['all_filters'] = {
            'languages': Language.objects.all(),
            'countries': Country.objects.all(),
            'topics': Topic.objects.all(),
        }

        return context

    @route(SCAN_URL)
    def scan_view(self, request):
        if request.method == 'POST':
            form = ScannerForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
            else:
                return HttpResponse('not cool')
            instance = SecuredropInstance(
                landing_page_domain=data['url'],
            )
            result = scanner.scan(instance)
            result.compute_grade()
            context = {
                'landing_page_domain': data['url'],
                'result': result,
                'submission_form': DirectoryForm(initial={
                    'url': data['url'],
                }),
                'submission_url': '{0}form/'.format(self.url),
                'org_details_form_title': self.org_details_form_title
            }

            if self.org_details_form_text:
                context['org_details_form_text'] = self.scanner_form_text

            return render(
                request,
                'landing_page_checker/result.html',
                context,
            )

        else:
            form = ScannerForm()

        context = {
            'form': form,
            'submit_url': '{base}{scan_url}'.format(base=self.url, scan_url=SCAN_URL),
            'form_title': self.scanner_form_title,
        }
        if self.scanner_form_text:
            context['text'] = self.scanner_form_text
        return render(request, 'directory/scanner_form.html', context)

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
                    onion_address=data['tor_address'],
                    live=False,
                )
                self.add_child(instance=instance)
                instance.save()
                result = scanner.scan(instance)
                result.save()

                return HttpResponseRedirect('{0}thanks/'.format(self.url))

        # else redirect to a page with errors
        else:
            form = DirectoryForm()
            context = {
                'form': form,
                'submit_url': '{0}form/'.format(self.url),
                'form_title': self.org_details_form_title
            }
            if self.org_details_form_text:
                context['text'] = self.org_details_form_text

        return render(
            request,
            'directory/directory_form.html',
            context
        )

    @route('thanks/')
    def thanks_view(self, request):
        context = {'thank_you_title': self.thank_you_title}
        if self.thank_you_text:
            context['text'] = self.thank_you_text
        return render(request, 'directory/thanks.html', context)
