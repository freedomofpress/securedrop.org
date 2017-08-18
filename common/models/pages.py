from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField

from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index


class PersonPage(Page):
    photo = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    bio = RichTextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('bio'),
        FieldPanel('website'),
        ImageChooserPanel('photo'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('bio'),
    ]
