from __future__ import unicode_literals

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
        self.slug = slugify(self.organization, allow_unicode=True)
        if len(self.slug) == 0:
            raise ValidationError('Slug must not be an empty string')
