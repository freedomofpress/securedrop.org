from django.db import models
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.text import slugify

from modelcluster.fields import ParentalKey
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailadmin.edit_handlers import (
    InlinePanel,
)

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
                data = form.cleaned_data
                # create secure_drop instance, adding parent page to the form
                instance = SecureDropInstance.objects.create(
                    page=self,
                    url=data['url'],
                    tor_address=data['tor_address'],
                )
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


class SecureDropInstance(Orderable):
    page = ParentalKey('directory.DirectoryPage', related_name='instances')
    landing_page = models.URLField(unique=True)
    onion_address = models.CharField(max_length=255, unique=True)

    organization = models.CharField('Organization', max_length=255, unique=True)
    slug = models.SlugField('Slug', unique=True, editable=False)

    added = models.DateTimeField(auto_now_add=True)

    def clean(self):
        self.slug = slugify(self.organization)

    def __str__(self):
        return '<SecureDropInstance {!r}>'.format(self.organization)


class Result(models.Model):
    # This is different from STN's Scan object in that each scan here will not
    # produce a new Result row. If multiple consecutive scans have the same
    # result, then we only insert that result once and set the result_last_seen
    # to the date of the last scan.
    securedrop = models.ForeignKey(SecureDropInstance, on_delete=models.CASCADE,
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

        self_values_to_compare = [(k,v) for k, v in self.__dict__.items()
                                  if k not in excluded_keys]
        other_values_to_compare = [(k,v) for k, v in other.__dict__.items()
                                   if k not in excluded_keys]

        return self_values_to_compare == other_values_to_compare

    def __str__(self):
        return 'Scan result for {}'.format(self.securedrop.organization)

    def compute_grade(self):
        if self.live == False:
            self.grade = '?'
            return

        if (self.forces_https == False or
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
        elif (self.hsts == False or
              self.expected_encoding == False or
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
