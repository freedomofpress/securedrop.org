from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from modelcluster.fields import ParentalManyToManyField, ParentalKey
from django.core.validators import RegexValidator

from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from autocomplete.edit_handlers import AutocompleteFieldPanel
from common.models.mixins import MetadataPageMixin


class SecuredropOwner(models.Model):
    page = ParentalKey(
        'landing_page_checker.SecuredropPage',
        related_name='owners'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='instances'
    )


class SecuredropPage(MetadataPageMixin, Page):
    landing_page_domain = models.URLField(
        'Landing Page Domain Name',
        max_length=255,
        unique=True
    )

    onion_address = models.CharField(
        'SecureDrop Onion Address',
        max_length=255,
        unique=True,
        validators=[RegexValidator(regex=r'\.onion$')]
    )

    added = models.DateTimeField(auto_now_add=True)

    organization_logo = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    organization_description = models.CharField(max_length=95, blank=True, null=True, help_text="A micro description of your organization that will be displayed in the directory.")

    languages = ParentalManyToManyField(
        'directory.Language',
        blank=True,
        verbose_name='Languages Accepted',
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
        verbose_name='Preferred Topics',
        related_name='topics'
    )

    content_panels = Page.content_panels + [
        FieldPanel('landing_page_domain'),
        FieldPanel('onion_address'),
        FieldPanel('organization_description'),
        ImageChooserPanel('organization_logo'),
        AutocompleteFieldPanel('languages', 'directory.Language'),
        AutocompleteFieldPanel('countries', 'directory.Country'),
        AutocompleteFieldPanel('topics', 'directory.Topic'),
        InlinePanel('owners')
    ]

    def get_live_result(self):
        # because results are ordered by date, returning the first one should be effective
        return Result.objects.filter(securedrop=self, live=True).first()


class Result(models.Model):
    # This is different from STN's Scan object in that each scan here will not
    # produce a new Result row. If multiple consecutive scans have the same
    # result, then we only insert that result once and set the result_last_seen
    # to the date of the last scan.
    securedrop = models.ForeignKey(SecuredropPage, on_delete=models.CASCADE,
                                   related_name='results')

    live = models.BooleanField()

    # In order to save a scan result when it is different from the last scan
    # we store result_last_scan
    result_last_seen = models.DateTimeField(auto_now_add=True)

    # HTTPS fields populated with pshtt
    forces_https = models.NullBooleanField()
    hsts = models.NullBooleanField()
    hsts_max_age = models.IntegerField(null=True, blank=True)
    hsts_entire_domain = models.NullBooleanField()
    hsts_preloaded = models.NullBooleanField()

    # Basic checks
    http_status_200_ok = models.NullBooleanField()
    http_no_redirect = models.NullBooleanField()
    expected_encoding = models.NullBooleanField()

    # Security headers
    no_server_info = models.NullBooleanField()
    no_server_version = models.NullBooleanField()
    csp_origin_only = models.NullBooleanField()
    mime_sniffing_blocked = models.NullBooleanField()
    noopen_download = models.NullBooleanField()
    xss_protection = models.NullBooleanField()
    clickjacking_protection = models.NullBooleanField()
    good_cross_domain_policy = models.NullBooleanField()
    http_1_0_caching_disabled = models.NullBooleanField()
    cache_control_set = models.NullBooleanField()
    cache_control_revalidate_set = models.NullBooleanField()
    cache_control_nocache_set = models.NullBooleanField()
    cache_control_notransform_set = models.NullBooleanField()
    cache_control_nostore_set = models.NullBooleanField()
    cache_control_private_set = models.NullBooleanField()
    expires_set = models.NullBooleanField()

    # Page content
    safe_onion_address = models.NullBooleanField()
    no_cdn = models.NullBooleanField()
    no_analytics = models.NullBooleanField()
    subdomain = models.NullBooleanField()
    no_cookies = models.NullBooleanField()

    grade = models.CharField(max_length=2, editable=False, default='?')

    class Meta:
        get_latest_by = 'result_last_seen'

    def __eq__(self, other):
        # Override Django's pk attribute equality
        # We will use the equality method to compare the scan results only

        excluded_keys = ['_state', '_securedrop_cache', 'result_last_seen',
                         'id', 'grade']

        self_values_to_compare = [(k, v) for k, v in self.__dict__.items()
                                  if k not in excluded_keys]
        other_values_to_compare = [(k, v) for k, v in other.__dict__.items()
                                   if k not in excluded_keys]

        return self_values_to_compare == other_values_to_compare

    def __str__(self):
        return 'Scan result for {}'.format(self.securedrop.title)

    def compute_grade(self):
        if self.live is False:
            self.grade = '?'
            return

        if (self.forces_https is False or
            self.no_cookies is False or
            self.http_no_redirect is False or
            self.http_status_200_ok is False or
            self.no_analytics is False):  # noqa: E129
            self.grade = 'F'
        elif (self.subdomain is True or
              self.no_cdn is False or
              self.no_server_info is False or
              self.no_server_version is False):
            self.grade = 'D'
        elif (self.hsts is False or
              self.expected_encoding is False or
              self.noopen_download is False or
              self.cache_control_set is False or
              self.csp_origin_only is False or
              self.mime_sniffing_blocked is False or
              self.xss_protection is False or
              self.clickjacking_protection is False or
              self.good_cross_domain_policy is False or
              self.http_1_0_caching_disabled is False or
              self.expires_set is False or
              self.hsts_max_age <= 16070400):
            self.grade = 'C'
        elif (self.cache_control_revalidate_set is False or
              self.cache_control_nocache_set is False or
              self.cache_control_notransform_set is False or
              self.cache_control_nostore_set is False or
              self.cache_control_private_set is False or
              self.hsts_preloaded is False or
              self.hsts_entire_domain is False):
            self.grade = 'B'
        else:
            self.grade = 'A'

    def save(self, *args, **kwargs):
            self.compute_grade()
            super(Result, self).save(*args, **kwargs)
