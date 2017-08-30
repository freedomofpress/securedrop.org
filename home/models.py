from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel

from common.models import MetadataPageMixin


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
            ],
            "Description"
        )
    ]


