from django.db import models
from modelcluster.fields import ParentalKey

from django.utils.html import strip_tags
from django.template.defaultfilters import truncatewords
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail import blocks
from wagtail.models import Page, Orderable
from wagtail.fields import StreamField, RichTextField

from common.models import MetadataPageMixin
from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
    AlignedImageBlock,
    AlignedEmbedBlock,
    RichTextBlockQuoteBlock,
    VideoBlock,
)
from search.utils import get_search_content_by_fields


class BaseSidebarPageMixin(models.Model):
    """
    A mixin that gives a model a sidebar menu field and the ability to
    intelligently use its own sidebar menu or a parent's sidebar menu.
    """

    sidebar_menu = models.ForeignKey(
        'menus.Menu',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='If left empty, page will use parent\'s sidebar menu'
    )

    settings_panels = [
        FieldPanel('sidebar_menu'),
    ]

    def get_sidebar_menu(self):
        """
        Return own sidebar menu if it exists. Otherwise, return the nearest
        ancestor's sidebar menu.
        """

        if self.sidebar_menu:
            return self.sidebar_menu

        try:
            return self.get_parent().specific.get_sidebar_menu()
        except AttributeError:
            return None

    class Meta:
        abstract = True


class SimplePage(MetadataPageMixin, Page):
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    body = StreamField(
        [

            ('text', blocks.RichTextBlock(
                features=[
                    'bold',
                    'italic',
                    'h2',
                    'h3',
                    'h4',
                    'ol',
                    'ul',
                    'hr',
                    'embed',
                    'link',
                    'document-link',
                    'image',
                    'code',
                ],
            )),
            ('image', AlignedImageBlock()),
            ('raw_html', blocks.RawHTMLBlock()),
            ('blockquote', RichTextBlockQuoteBlock()),
            ('list', blocks.ListBlock(
                blocks.CharBlock(label="List Item"),
                template='common/blocks/list_block_columns.html'
            )),
            ('video', AlignedEmbedBlock()),
            ('media_file', VideoBlock()),
            ('heading_1', Heading1()),
            ('heading_2', Heading2()),
            ('heading_3', Heading3()),
        ],
        blank=False,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
    ]

    search_fields_pgsql = ['title', 'body']

    def get_search_content(self):
        return get_search_content_by_fields(self, self.search_fields_pgsql)

    def get_meta_description(self):
        if self.search_description:
            return self.search_description

        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )


class SimplePageWithMenuSidebar(MetadataPageMixin, BaseSidebarPageMixin, Page):
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    body = StreamField(
        [
            ('text', blocks.RichTextBlock(
                features=[
                    'bold',
                    'italic',
                    'h2',
                    'h3',
                    'h4',
                    'ol',
                    'ul',
                    'hr',
                    'embed',
                    'link',
                    'document-link',
                    'image',
                    'code',
                ],
            )),
            ('image', AlignedImageBlock()),
            ('raw_html', blocks.RawHTMLBlock()),
            ('blockquote', RichTextBlockQuoteBlock()),
            ('list', blocks.ListBlock(
                blocks.CharBlock(label="List Item"),
                template='common/blocks/list_block_columns.html'
            )),
            ('video', AlignedEmbedBlock()),
            ('media_file', VideoBlock()),
            ('heading_1', Heading1()),
            ('heading_2', Heading2()),
            ('heading_3', Heading3()),
        ],
        blank=False,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
    ]

    settings_panels = Page.settings_panels + BaseSidebarPageMixin.settings_panels

    search_fields_pgsql = ['title', 'body']

    def get_search_content(self):
        return get_search_content_by_fields(self, self.search_fields_pgsql)

    def get_meta_description(self):
        if self.search_description:
            return self.search_description

        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )


class FAQPage(MetadataPageMixin, BaseSidebarPageMixin, Page):
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    body = StreamField(
        [
            ('text', blocks.RichTextBlock(
                features=[
                    'bold',
                    'italic',
                    'h2',
                    'h3',
                    'h4',
                    'ol',
                    'ul',
                    'hr',
                    'embed',
                    'link',
                    'document-link',
                    'image',
                    'code',
                ],
            )),
            ('image', AlignedImageBlock()),
            ('raw_html', blocks.RawHTMLBlock()),
            ('blockquote', RichTextBlockQuoteBlock()),
            ('list', blocks.ListBlock(
                blocks.CharBlock(label="List Item"),
                template='common/blocks/list_block_columns.html'
            )),
            ('video', AlignedEmbedBlock()),
            ('media_file', VideoBlock()),
            ('heading_1', Heading1()),
            ('heading_2', Heading2()),
            ('heading_3', Heading3()),
        ],
        blank=True,
        null=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
        InlinePanel('questions', label="Questions")
    ]

    settings_panels = Page.settings_panels + BaseSidebarPageMixin.settings_panels


class FaqQuestion(Orderable):
    page = ParentalKey('simple.FAQPage', related_name='questions')
    question = models.CharField(max_length=255)
    # features disables h1 use
    answer = RichTextField(
        features=['h2', 'h3', 'bold', 'italic', 'link', 'embed', 'image', 'embed', 'document-link', 'ol', 'ul', 'code']
    )
