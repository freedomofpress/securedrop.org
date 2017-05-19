from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Securedrop(models.Model):
    organization = models.CharField('Organization', max_length=255, unique=True)
    slug = models.SlugField('Slug', unique=True, editable=False)

    landing_page_domain = models.CharField(
        'Landing Page Domain Name',
        max_length=255,
        unique=True)

    onion_address = models.CharField(
        'SecureDrop Onion Address',
        max_length=255,
        unique=True)

    added = models.DateTimeField(auto_now_add=True)

    def clean(self):
        self.slug = slugify(self.organization)

    def __str__(self):
        return 'SecureDrop: {}'.format(self.organization)


class Result(models.Model):
    # This is different from STN's Scan object in that each scan here will not
    # produce a new Result row. If multiple consecutive scans have the same
    # result, then we only insert that result once and set the result_last_seen
    # to the date of the last scan.
    securedrop = models.ForeignKey(Securedrop, on_delete=models.CASCADE,
                                   related_name='results')

    live = models.BooleanField()

    # In order to save a scan result when it is different from the last scan
    # we store result_last_scan
    result_last_seen = models.DateTimeField(auto_now_add=True)

    # HTTPS fields populated with pshtt
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

    def __str__(self):
        return 'Result for {} , last seen {:%Y-%m-%d %H:%M}'.format(
            self.securedrop.organization, self.result_last_seen)

    def compute_grade(self):
        if self.live == False:
            self.grade = '?'
            return

        if (self.hsts == False or
            self.no_cookies == False or
            self.http_no_redirect == False or
            self.http_status_200_ok == False or
            self.no_analytics == False):
            self.grade = 'F'
        elif (self.subdomain == True or
              self.no_cdn == False or
              self.no_server_info == False or
              self.no_server_version == False):
            self.grade = 'D'
        elif (self.expected_encoding == False or
              self.noopen_download == False or
              self.cache_control_set == False or
              self.csp_origin_only == False or
              self.mime_sniffing_blocked == False or
              self.xss_protection == False or
              self.clickjacking_protection == False or
              self.good_cross_domain_policy == False or
              self.http_1_0_caching_disabled == False or
              self.expires_set == False or
              self.hsts_max_age <= 16070400):
            self.grade = 'C'
        elif (self.cache_control_revalidate_set == False or
              self.cache_control_nocache_set == False or
              self.cache_control_notransform_set == False or
              self.cache_control_nostore_set == False or
              self.cache_control_private_set == False or
              self.hsts_preloaded == False or
              self.hsts_entire_domain == False):
            self.grade = 'B'
        else:
            self.grade = 'A'

    def save(self, *args, **kwargs):
            self.compute_grade()
            super(Result, self).save(*args, **kwargs)
