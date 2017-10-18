from django.db import models
from django.utils.html import strip_tags
from django.template.defaultfilters import truncatewords

from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsearch import index
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route

from blog.feeds import BlogIndexPageFeed
from common.utils import DEFAULT_PAGE_KEY, paginate
from common.models import MetadataPageMixin
from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
    AlignedImageBlock,
    AlignedEmbedBlock,
    RichTextBlockQuoteBlock,
    CodeBlock,
)
from github.models import Release


class BlogPage(MetadataPageMixin, Page):
    publication_datetime = models.DateTimeField(
        help_text='Past or future date of publication'
    )

    body = StreamField(
        [
            ('text', blocks.RichTextBlock()),
            ('code', CodeBlock(label='Code Block')),
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

    category = models.ForeignKey(
        # Likely a CategoryPage
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    release = models.OneToOneField(
        'github.Release',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_page',
        help_text='Releases can be associated with only one post, which should be a release announcement.'
    )

    content_panels = Page.content_panels + [
        FieldPanel('publication_datetime'),
        StreamFieldPanel('body'),
        MultiFieldPanel(
            heading='Teaser',
            children=[
                FieldPanel('teaser_text'),
            ]
        ),
        PageChooserPanel('author', 'common.PersonPage'),
        PageChooserPanel('category', 'blog.CategoryPage'),
        FieldPanel('release'),
    ]

    parent_page_types = ['blog.BlogIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('body', partial=True),
        index.SearchField('teaser_text'),
        index.FilterField('publication_datetime'),
    ]

    def get_meta_description(self):
        if self.teaser_text:
            return strip_tags(self.teaser_text)

        if self.search_description:
            return self.search_description

        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )


class CategoryPage(MetadataPageMixin, Page):
    description = RichTextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('description'),
    ]

    parent_page_types = ['blog.BlogIndexPage']

    def get_blog_posts(self):
        return BlogPage.objects.live().filter(category=self)

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


class BlogIndexPage(RoutablePageMixin, MetadataPageMixin, Page):
    body = StreamField(
        [
            ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
            ('image', ImageChooserBlock()),
            ('raw_html', blocks.RawHTMLBlock()),
        ],
        blank=True
    )

    link_to_page_text = models.CharField(
        max_length=100,
        default="Read More",
        help_text="Text to display at the bottom of blog teasers that links to the blog page."
    )

    release_title = models.CharField(
        max_length=100,
        default="Current Release",
        help_text="Text to display as a title for the current release in the sidebar.")

    feed_limit = models.PositiveIntegerField(
        default=20,
        help_text='Maximum number of posts to be included in the '
                  'syndication feed. 0 for unlimited.'
    )

    # pagination
    per_page = models.PositiveIntegerField(
        default=8,
        help_text="Number of posts to display per page."
    )
    orphans = models.PositiveIntegerField(
        default=5,
        help_text="Number of posts to append to the last page to prevent there being a small last page."
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('feed_limit'),
        FieldPanel('link_to_page_text'),
        FieldPanel('release_title'),
        MultiFieldPanel(
            [
                FieldPanel('per_page'),
                FieldPanel('orphans')
            ],
            'Pagination'
        )
    ]

    subpage_types = ['blog.BlogPage', 'blog.CategoryPage']

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
            per_page=self.per_page,
            orphans=self.orphans
        )

        context['entries_page'] = entries
        context['paginator'] = paginator

        return context

    def get_meta_description(self):
        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )

    def get_category_pages(self):
        return CategoryPage.objects.live()

    def get_current_release(self):
        return Release.objects.order_by('-date').first()
