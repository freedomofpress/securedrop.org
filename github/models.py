from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailsnippets.models import register_snippet


@register_snippet
class Release(models.Model):
    url = models.URLField(blank=False, null=False)
    tag_name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )
    date = models.DateTimeField(blank=False, null=False)

    panels = [
        FieldPanel('url'),
        FieldPanel('tag_name'),
        FieldPanel('date'),
    ]

    def __str__(self):
        return '{} released at {} ({})'.format(
            self.tag_name,
            self.date,
            self.url,
        )
