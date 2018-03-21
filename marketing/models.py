from django.db import models
from modelcluster.fields import ParentalKey

from common.models import MetadataPageMixin
from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
    AlignedImageBlock,
    AlignedEmbedBlock,
    RichTextBlockQuoteBlock,
)
from search.utils import get_search_content_by_fields

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


class MarketingIndexPage(MetadataPageMixin, Page):
    subtitle = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Appears immediately below page title."

    )
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
        null=True,
        blank=True
    )

    subheader = models.CharField(
        max_length=255,
        default="How to install SecureDrop at your organization.",
        help_text="Displayed below features."
    )

    how_to_install_subtitle = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Appears immediately below subheader."

    )

    how_to_install_body = StreamField(
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
        null=True,
        blank=True
    )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        StreamFieldPanel('body'),
        InlinePanel('features', label="Features"),
        MultiFieldPanel(
            heading='How to install',
            children=[
                FieldPanel('subheader'),
                FieldPanel('how_to_install_subtitle'),
                StreamFieldPanel('how_to_install_body'),
            ]
        ),
    ]

    subpage_types = ['marketing.FeaturePage']

    search_fields_pgsql = ['title', 'body', 'subheader']

    def get_search_content(self):
        search_content = get_search_content_by_fields(self, self.search_fields_pgsql)

        for feature in self.features.all():
            search_content += feature.feature.title + ' '
            search_content += feature.feature.teaser_title + ' '
            search_content += feature.feature.teaser_description + ' '

        return search_content


class OrderedFeatures(Orderable):
    page = ParentalKey(
        'marketing.MarketingIndexPage',
        related_name='features'
    )
    feature = models.ForeignKey(
        'marketing.FeaturePage',
        related_name='marketing_order'
    )

    panels = [
        PageChooserPanel('feature')
    ]

    class Meta:
        unique_together = (('page', 'feature'),)


class FeaturePage(MetadataPageMixin, Page):
    teaser_title = models.CharField(max_length=60)
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

    parent_page_types = ['marketing.MarketingIndexPage']

    content_panels = Page.content_panels + [
        FieldPanel('teaser_title'),
        ImageChooserPanel('icon'),
        FieldPanel('teaser_description'),
        FieldPanel('description'),
    ]

    search_fields_pgsql = ['title', 'teaser_title', 'teaser_description', 'description']

    def get_search_content(self):
        return get_search_content_by_fields(self, self.search_fields_pgsql)

    def sort_order(self):
        return self.marketing_order.get(page=self.get_parent()).sort_order

    def next(self):
        ordered_feature = OrderedFeatures.objects.filter(
            page=self.get_parent(),
            sort_order__gt=self.sort_order()).first()
        if ordered_feature:
            return ordered_feature.feature
        return None

    def previous(self):
        ordered_feature = OrderedFeatures.objects.filter(
            page=self.get_parent(),
            sort_order__lt=self.sort_order()).last()
        if ordered_feature:
            return ordered_feature.feature
        return None

    def all_features(self):
        return self.get_parent().specific.features.all()

    def __str__(self):
        return self.teaser_title
