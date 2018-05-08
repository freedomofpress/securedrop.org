from django.db import models
from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel, InlinePanel

from common.models import MetadataPageMixin, Button
from search.utils import get_search_content_by_fields
from search.utils.documentation import READTHEDOCS_BASE
from blog.models import BlogPage
from github.models import Release


class HomePage(MetadataPageMixin, Page):
    description_header = models.CharField(max_length=255, default="Share and accept documents securely.")
    # Disables headers and image/video embeds
    description = RichTextField(
        features=['bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link'],
        blank=True,
        null=True
    )
    features_header = models.CharField(
        max_length=255,
        default="What SecureDrop Does"
    )
    instances_header = models.CharField(
        max_length=255,
        default="Share Documents Securely With These Organizations"
    )
    instances_button = models.ForeignKey(
        'home.InstancesButton',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    instance_link_default_text = models.CharField(
        max_length=255,
        default="View in the directory",
        help_text="Text displayed linking to each instance's page in the directory."
    )

    search_fields_pgsql = ['title', 'description', 'features_header', 'instances_header']

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
                    label="Highlighted Features",
                    max_num=6
                ),
                InlinePanel('features_button', label="Features Button", max_num=1)
            ],
            "Features",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('instances_header'),
                InlinePanel('instances', label="Instances", max_num=6),
                InlinePanel('instance_button', label="Button", max_num=1),
                FieldPanel('instance_link_default_text')
            ],
            "Highlighted Instances",
            classname="collapsible"
        ),
    ]

    def get_search_content(self):
        search_content = get_search_content_by_fields(self, self.search_fields_pgsql)

        for hp_feature in self.features.all():
            search_content += hp_feature.feature.title + ' '

        for hp_instance in self.instances.all():
            search_content += hp_instance.instance.title + ' '

        return search_content

    def get_latest_blog(self):
        return BlogPage.objects.live().order_by('-publication_datetime').first()

    def get_current_release(self):
        return Release.objects.order_by('-date').first()

    def docs_url(self):
        return READTHEDOCS_BASE


class DescriptionButtons(Orderable, Button):
    page = ParentalKey('home.HomePage', related_name='description_buttons')

    panels = [
        FieldPanel('text'),
        PageChooserPanel('link')
    ]


class InstancesButton(Button):
    page = ParentalKey('home.HomePage', related_name='instance_button')

    panels = [
        FieldPanel('text'),
        PageChooserPanel('link')
    ]


class FeaturesButton(Button):
    page = ParentalKey('home.HomePage', related_name='features_button')

    panels = [
        FieldPanel('text'),
        PageChooserPanel('link')
    ]


class HomepageFeature(Orderable):
    page = ParentalKey('home.HomePage', related_name='features')
    feature = models.ForeignKey(
        'marketing.FeaturePage',
        related_name='+'
    )

    panels = [
        PageChooserPanel('feature')
    ]

    class Meta:
        unique_together = (('page', 'feature'),)


class HomePageInstances(Orderable):
    page = ParentalKey('home.HomePage', related_name='instances')
    instance = models.ForeignKey(
        'directory.DirectoryEntry',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('instance'),
    ]
