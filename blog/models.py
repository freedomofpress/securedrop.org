from django.db import models
from django.utils.html import strip_tags
from django.template.defaultfilters import truncatewords

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from blog.feeds import BlogIndexPageFeed
from common.utils import DEFAULT_PAGE_KEY, paginate
from search.utils import get_search_content_by_fields
from common.models import MetadataPageMixin
from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
    InlinePDFBlock,
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
            ('inline_pdf', InlinePDFBlock()),
        ],
        blank=False
    )

    teaser_text = RichTextField(
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        # Likely a CategoryPage
        'wagtailcore.Page',
        on_delete=models.PROTECT,
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
        PageChooserPanel('category', 'blog.CategoryPage'),
        FieldPanel('release'),
    ]

    parent_page_types = ['blog.BlogIndexPage']

    search_fields_pgsql = ['title', 'body', 'teaser_text', 'category']

    class Meta:
        indexes = [
            models.Index(fields=['publication_datetime']),
            models.Index(fields=['category']),
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

    def get_search_content(self):
        return get_search_content_by_fields(self, self.search_fields_pgsql)


class CategoryPage(MetadataPageMixin, Page):
    description = RichTextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('description'),
    ]

    search_fields_pgsql = ['title', 'description']

    parent_page_types = ['blog.BlogIndexPage']

    def get_posts(self):
        return BlogPage.objects.filter(category=self)\
            .sibling_of(self, inclusive=False)\
            .live()\
            .order_by('-publication_datetime')

    def get_context(self, request):
        context = super(CategoryPage, self).get_context(request)

        entry_qs = self.get_posts()
        # Use parent's settings for pagination counts
        parent = self.get_parent().specific

        paginator, entries = paginate(request, entry_qs,
                                      page_key=DEFAULT_PAGE_KEY,
                                      per_page=parent.per_page,
                                      orphans=parent.orphans)

        context['entries_page'] = entries
        context['paginator'] = paginator

        return context

    def get_search_content(self):
        return get_search_content_by_fields(self, self.search_fields_pgsql)


class BlogIndexPage(RoutablePageMixin, MetadataPageMixin, Page):
    subtitle = models.CharField(max_length=255, null=True, blank=True)

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
        help_text="Minimum number of stories on the last page (if the last page is smaller, they will get added to the preceding page)."
    )

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
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

    search_fields_pgsql = ['title', 'body']

    def get_search_content(self):
        search_elements = get_search_content_by_fields(self, self.search_fields_pgsql)

        for blog_page in self.get_posts():
            search_elements.append(blog_page.title)

        return search_elements

    @route(r'^feed/$')
    def feed(self, request):
        return BlogIndexPageFeed(self)(request)

    def get_posts(self):
        return BlogPage.objects.child_of(self).live().order_by('-publication_datetime')

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
        return CategoryPage.objects.child_of(self).live()

    def get_current_release(self):
        return Release.objects.order_by('-date').first()

    def get_cached_paths(self):
        yield self.url
        yield self.url + self.reverse_subpage('feed')
        page_count = self.get_posts().count() // self.per_page
        for x in range(1, page_count + 2):
            yield '{}?page={}'.format(self.url, x)
