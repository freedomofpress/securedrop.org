from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel


@register_setting
class FooterSettings(BaseSetting):
    title = RichTextField(blank=True, null=True)
    main_menu = models.ForeignKey(
        'menus.Menu',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    release_key = models.CharField(max_length=255, default='Key is unavailable')
    release_key_description = models.CharField(
        max_length=255,
        default="SecureDrop Release Signing Key \n (Not for communication)"
    )
    release_key_link = models.URLField(blank=True, null=True)
    support_title = models.CharField(max_length=100, default="Get Support")
    support_menu = models.ForeignKey(
        'menus.Menu',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    donation_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    contribute_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    panels = [
        FieldPanel('title'),
        SnippetChooserPanel('main_menu'),
        PageChooserPanel('donation_link'),
        PageChooserPanel('contribute_link'),
        MultiFieldPanel(
            [
                FieldPanel('release_key_description'),
                FieldPanel('release_key'),
                FieldPanel('release_key_link'),
            ],
            "Release Key",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('support_title'),
                SnippetChooserPanel('support_menu'),
            ],
            "Support Footer Settings",
            classname="collapsible"
        ),
    ]

    class Meta:
        verbose_name = 'Site Footer'


@register_setting(icon='warning')
class AlertSettings(BaseSetting):
    title = models.CharField(max_length=100, default='Alert')
    body = RichTextField(blank=True, null=True)
    close_text = models.CharField(
        max_length=100,
        default='Close Alert',
        help_text='Text on the close button visible only to screenreaders.'
    )
    display_alert = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Site Alert'


@register_setting(icon='plus')
class SocialSharingSEOSettings(BaseSetting):
    default_description = models.TextField(
        blank=True,
        null=True,
        help_text='Default text description for pages that don\'t have another '
                  'logical field for text descirptions'
    )

    default_image = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Default image for pages that don\'t have another '
                  'logical image for social sharing'
    )

    facebook_page_id = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text='Find on your Facebook page by navigating to "About" and '
                  'scrolling to the bottom'
    )

    twitter = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text='Your Twitter username'
    )

    panels = [
        FieldPanel('default_description'),
        ImageChooserPanel('default_image'),
        FieldPanel('facebook_page_id'),
        FieldPanel('twitter'),
    ]

    class Meta:
        verbose_name = 'Social Sharing/SEO'


@register_setting(icon='form')
class DirectorySettings(BaseSetting):
    landing_page_link_text = models.CharField(
        max_length=255,
        default='Securedrop landing page'
    )
    compare_onion_address_text = models.CharField(
        max_length=255,
        default='Check this address against the one on the landing page:',
        help_text='Text displayed immedieately before the onion address.'
    )
    grade_text = models.CharField(
        max_length=100,
        default='Security Grade'
    )
    security_warning = RichTextField(
        blank=True,
        null=True,
        help_text="Warning displayed for sources on instance pages."
    )
    no_results_text = RichTextField(
        default='Results could not be calculated.',
        help_text='Text displayed when there are no results for a results group.'
    )

    panels = [
        FieldPanel('landing_page_link_text'),
        FieldPanel('compare_onion_address_text'),
        FieldPanel('grade_text'),
        FieldPanel('security_warning'),
        FieldPanel('no_results_text')
    ]

    class Meta:
        verbose_name = 'Directory Settings'
