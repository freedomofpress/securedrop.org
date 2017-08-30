from django.db import models
from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel, InlinePanel

from common.models import MetadataPageMixin, Button


class HomePage(MetadataPageMixin, Page):
    description_header = models.CharField(max_length=255, blank=True, null=True)
    # Disables headers and image/video embeds
    description = RichTextField(
        features=['bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link' ],
        blank=True,
        null=True
    )

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
        )
    ]


class DescriptionButtons(Orderable, Button):
    page = ParentalKey('home.HomePage', related_name='description_buttons')

    panels = [
        FieldPanel('text'),
        PageChooserPanel('link')
    ]
