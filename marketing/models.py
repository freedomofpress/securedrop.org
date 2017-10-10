from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from common.models import MetadataPageMixin
from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
    AlignedImageBlock,
    AlignedEmbedBlock,
    RichTextBlockQuoteBlock,
)

from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


class MarketingIndexPage(MetadataPageMixin, Page):
    body = StreamField(
        [
            ('text', blocks.RichTextBlock()),
            ('image', AlignedImageBlock()),
            ('raw_html', blocks.RawHTMLBlock()),
            ('blockquote', RichTextBlockQuoteBlock()),
            ('list', blocks.ListBlock(
                blocks.CharBlock(label="List Item"),
                template='common/blocks/list_block_columns.html'
            )),
            ('video', AlignedEmbedBlock()),
            ('heading_1', Heading1()),
            ('heading_2', Heading2()),
            ('heading_3', Heading3()),
        ],
        blank=False
    )

    subheader = models.CharField(
        max_length=255,
        default="How to install SecureDrop at your organization.",
        help_text="Displayed below features and before the body."
    )

    content_panels = Page.content_panels + [
        FieldPanel('subheader'),
        StreamFieldPanel('body'),
    ]

    subpage_types = ['marketing.FeaturePage']


class FeaturePage(MetadataPageMixin, Page):
    icon = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    teaser_description = models.CharField(
        max_length=255,
        help_text="A one sentence description displayed with the feature overview."
    )
    description = RichTextField(
        features=['bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link'],
        blank=True,
        null=True
    )

    sort_order = models.PositiveIntegerField(null=True, blank=True, unique=True, help_text="Determines what order pages will be displayed in.")
    sort_order_field = 'sort_order'

    parent_page_types = ['marketing.MarketingIndexPage']

    content_panels = Page.content_panels +  [
        ImageChooserPanel('icon'),
        FieldPanel('teaser_description'),
        FieldPanel('description'),
        FieldPanel('sort_order')
    ]

    class Meta:
        ordering = ['sort_order']

    def next(self):
        try:
            return FeaturePage.objects.get(sort_order=self.sort_order + 1)
        except(ObjectDoesNotExist):
            return None

    def previous(self):
        try:
            return FeaturePage.objects.get(sort_order=self.sort_order - 1)
        except(ObjectDoesNotExist):
            return None

    def all_features(self):
        return FeaturePage.objects.live()

    def __str__(self):
        return '%s. %s' % (self.sort_order, self.title)
