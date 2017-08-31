from django.db import models
from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from common.models import MetadataPageMixin, Button


class HomePage(MetadataPageMixin, Page):
    description_header = models.CharField(max_length=255, blank=True, null=True)
    # Disables headers and image/video embeds
    description = RichTextField(
        features=['bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link'],
        blank=True,
        null=True
    )
    features_header = models.CharField(max_length=255, blank=True, null=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('description_header'),
                FieldPanel('description'),
                InlinePanel(
                    'description_buttons',
                    label="Links",
                    max_num=2,
                )
            ],
            "Description",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('features_header'),
                InlinePanel(
                    'features',
                    label="SecureDrop Features",
                    max_num=8
                ),
            ],
            "Features",
            classname="collapsible"
        )
    ]


class DescriptionButtons(Orderable, Button):
    page = ParentalKey('home.HomePage', related_name='description_buttons')

    panels = [
        FieldPanel('text'),
        PageChooserPanel('link')
    ]


class Feature(Orderable):
    page = ParentalKey('home.HomePage', related_name='features')
    icon = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    description = RichTextField(
        features=['bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link'],
        blank=True,
        null=True
    )

    panels = [
        ImageChooserPanel('icon'),
        FieldPanel('title'),
        FieldPanel('description')
    ]
