from django.db import models

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, InlinePanel, MultiFieldPanel
from wagtail.wagtailcore.models import Orderable
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet


@register_snippet
class Menu(ClusterableModel):
    name = models.CharField(max_length=255, help_text='A name to identify this menu by for internal use')
    slug = models.SlugField(max_length=255, help_text='A key to identify this menu in code')

    panels = [
        MultiFieldPanel((
            FieldPanel('name'),
            FieldPanel('slug'),
        ), 'Details'),
        InlinePanel('menu_items', label="Menu Items"),
    ]

    def __str__(self):
        return self.name


class MenuItem(Orderable):
    text = models.CharField(max_length=255)
    link_page = models.ForeignKey('wagtailcore.Page', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    link_document = models.ForeignKey('wagtaildocs.Document', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    link_url = models.CharField(blank=True, max_length=255, help_text='A URL or path for this menu item to link to.')
    html_title = models.CharField(blank=True, max_length=255, help_text='Value for the HTML title attribute')
    html_classes = models.CharField(blank=True, max_length=255, help_text='HTML classes to be added to this menu item')
    menu = ParentalKey(Menu, related_name='menu_items')

    panels = [
        FieldPanel('text'),
        MultiFieldPanel((
            PageChooserPanel('link_page'),
            DocumentChooserPanel('link_document'),
            FieldPanel('link_url'),
        ), 'Destination'),
        MultiFieldPanel((
            FieldPanel('html_title'),
            FieldPanel('html_classes'),
        ), 'HTML')
    ]

    @property
    def url(self):
        """
        Return an available url in this order of priority: page, document, raw url.
        """

        if self.link_page:
            return self.link_page.url
        if self.link_document:
            return self.link_document.url
        return self.link_url
