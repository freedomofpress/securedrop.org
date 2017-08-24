from django.db import models
from django.utils.html import strip_tags
from django.template.defaultfilters import truncatewords

from modelcluster.fields import ParentalManyToManyField

from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route

from blog.feeds import BlogIndexPageFeed
from common.utils import DEFAULT_PAGE_KEY, paginate
from common.models import MetadataPageMixin
from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
    StyledTextBlock,
    AlignedImageBlock,
    AlignedEmbedBlock,
    RichTextBlockQuoteBlock,
)


class BlogIndexPage(RoutablePageMixin, MetadataPageMixin, Page):
    body = StreamField(
        [
            ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
            ('image', ImageChooserBlock()),
            ('raw_html', blocks.RawHTMLBlock()),
        ],
        blank=True
    )

    feed_limit = models.PositiveIntegerField(
        default=20,
        help_text='Maximum number of posts to be included in the '
                  'syndication feed. 0 for unlimited.'
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('feed_limit'),
    ]

    subpage_types = ['blog.BlogPage']

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    @route(r'^feed/$')
    def feed(self, request):
        return BlogIndexPageFeed(self)(request)

    def get_posts(self):
        return BlogPage.objects.child_of(self)\
                       .live()\
                       .order_by('-publication_datetime')

    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)
        entry_qs = self.get_posts()

        paginator, entries = paginate(
            request,
            entry_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=8,
            orphans=5
        )

        context['entries_page'] = entries
        context['paginator'] = paginator

        return context

    def get_meta_description(self):
        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )


class BlogPage(MetadataPageMixin, Page):
    publication_datetime = models.DateTimeField(
        help_text='Past or future date of publication'
    )

    body = StreamField(
        [
            ('text', StyledTextBlock(label='Text', template='common/blocks/styled_text_full_bleed.html')),
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

    teaser_image = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    teaser_text = RichTextField(
        null=True,
        blank=True
    )

    author = models.ForeignKey(
        # Likely a PersonPage
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    categories = ParentalManyToManyField('blog.CategoryPage', blank=True)

    release = models.ForeignKey(
        'github.Release',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='posts',
    )

    content_panels = Page.content_panels + [
        FieldPanel('publication_datetime'),
        StreamFieldPanel('body'),
        MultiFieldPanel(
            heading='Teaser',
            children=[
                ImageChooserPanel('teaser_image'),
                FieldPanel('teaser_text'),
            ]
        ),
        PageChooserPanel('author', 'common.PersonPage'),
        FieldPanel('categories'),
    ]

    parent_page_types = ['blog.BlogIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('body', partial=True),
        index.SearchField('teaser_text'),
        index.FilterField('publication_datetime'),
    ]

    def get_meta_image(self):
        return self.teaser_image or super(BlogPage, self).get_meta_image()

    def get_meta_description(self):
        if self.teaser_text:
            return strip_tags(self.teaser_text)

        if self.search_description:
            return self.search_description

        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )


class CategoryPage(Page):
    description = RichTextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('description'),
    ]

    def get_blog_posts(self):
        return BlogPage.objects.live().filter(categories=self)

    def get_context(self, request):
        context = super(CategoryPage, self).get_context(request)

        entry_qs = self.get_blog_posts()
        # Use parent's settings for pagination counts
        parent = self.get_parent().specific

        paginator, entries = paginate(request, entry_qs,
                                      page_key=DEFAULT_PAGE_KEY,
                                      per_page=parent.per_page,
                                      orphans=parent.orphans)

        context['entries_page'] = entries
        context['paginator'] = paginator

        return context
