from __future__ import unicode_literals

from django.db import models
from django.db.models import Func, F, Value
from modelcluster.fields import ParentalManyToManyField
from django.core.validators import RegexValidator

from wagtail.wagtailcore.models import Page, PageManager, PageQuerySet
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from autocomplete.edit_handlers import AutocompleteFieldPanel
from common.models.mixins import MetadataPageMixin
from search.utils import get_search_content_by_fields
from common.models.edit_handlers import ReadOnlyPanel


class SecuredropPageQuerySet(PageQuerySet):
    def with_domain_annotation(self):
        """
        Return the queryset with a `domain` field annotated on containing the
        domain as extracted from the `landing_page_domain` field
        """

        # Assuming all landing_page_domains include http:// or https:// as a
        # protocol (as enforced by URLField logic) we can count on the domain
        # being the third token when splitting on '/'
        return self.annotate(
            domain=Func(
                F('landing_page_domain'),
                Value('/'),
                Value(3),
                function='SPLIT_PART'
            )
        )


class SecuredropPageManager(PageManager):
    """
    This thin manager class is necessary for Wagtail 1.12.
    (See: https://github.com/wagtail/wagtail/pull/3557) After upgrading past
    Wagtail 1.13, this can be replaced with the following line of code:

        SecuredropPageManager = PageManager.from_queryset(SecuredropPageQuerySet)
    """

    def get_queryset(self):
        return SecuredropPageQuerySet(self.model)


SecuredropPageManager = SecuredropPageManager.from_queryset(SecuredropPageQuerySet)


class SecuredropPage(MetadataPageMixin, Page):
    objects = SecuredropPageManager()

    landing_page_domain = models.URLField(
        'Landing page domain name',
        max_length=255,
        unique=True
    )

    onion_address = models.CharField(
        'SecureDrop onion address',
        max_length=255,
        validators=[RegexValidator(regex=r'\.onion$', message="Enter a valid .onion address.")]
    )

    added = models.DateTimeField(auto_now_add=True)

    organization_logo = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    organization_logo_homepage = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Optional second logo optimized to show up on dark backgrounds. For instances that are featured on the homepage.'
    )

    organization_description = models.CharField(max_length=95, blank=True, null=True, help_text="A micro description of your organization that will be displayed in the directory.")

    languages = ParentalManyToManyField(
        'directory.Language',
        blank=True,
        verbose_name='Languages accepted',
        related_name='languages'
    )

    countries = ParentalManyToManyField(
        'directory.Country',
        blank=True,
        verbose_name='Countries',
        related_name='countries'
    )

    topics = ParentalManyToManyField(
        'directory.Topic',
        blank=True,
        verbose_name='Preferred topics',
        related_name='topics'
    )

    content_panels = Page.content_panels + [
        ReadOnlyPanel('added', label='Date Added'),
        FieldPanel('landing_page_domain'),
        FieldPanel('onion_address'),
        FieldPanel('organization_description'),
        ImageChooserPanel('organization_logo'),
        ImageChooserPanel('organization_logo_homepage'),
        AutocompleteFieldPanel('languages', 'directory.Language'),
        AutocompleteFieldPanel('countries', 'directory.Country'),
        AutocompleteFieldPanel('topics', 'directory.Topic'),
        InlinePanel('owners', label='Owners'),
        InlinePanel('results', label='Results'),
    ]

    search_fields_pgsql = ['title', 'landing_page_domain', 'onion_address', 'organization_description']

    def serve(self, request):
        owners = [sd_owner.owner for sd_owner in self.owners.all()]
        if request.user in owners:
            self.editable = True
        else:
            self.editable = False

        return super(SecuredropPage, self).serve(request)

    def get_live_result(self):
        # Used in template to get the latest live result.
        return self.results.filter(live=True).latest()

    def get_search_content(self):
        search_content = get_search_content_by_fields(self, self.search_fields_pgsql)

        for field in ['languages', 'countries', 'topics']:
            titles = [item.title for item in getattr(self, field).all()]
            search_content += " ".join(titles) + ' '

        return search_content

    def save(self, *args, **kwargs):
        from directory.models import Result
        super(SecuredropPage, self).save(*args, **kwargs)
        self.results = Result.objects.filter(landing_page_domain=self.landing_page_domain)
