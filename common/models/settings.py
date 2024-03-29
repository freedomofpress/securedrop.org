from django.conf import settings
from django.db import models

from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField


@register_setting
class FooterSettings(BaseSiteSetting):
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
    donation_url = models.URLField()
    contribute_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    twitter_url = models.URLField(
        blank=True,
        help_text='Link to Twitter profile',
    )
    mastodon_url = models.URLField(
        blank=True,
        help_text='Link to Mastodon profile',
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('main_menu'),
        FieldPanel('donation_url'),
        FieldPanel('contribute_link'),
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
                FieldPanel('support_menu'),
            ],
            "Support Footer Settings",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('twitter_url'),
                FieldPanel('mastodon_url'),
            ],
            'Social Media',
            classname='collapsible'
        ),
    ]

    class Meta:
        verbose_name = 'Site Footer'

    @property
    def securedrop_onion_address(self):
        return settings.ONION_HOSTNAME


@register_setting(icon='warning')
class AlertSettings(BaseSiteSetting):
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


@register_setting(icon='warning')
class TorAlertSettings(BaseSiteSetting):
    title = models.CharField(
        max_length=255,
        default="Have a document to share?",
        help_text="Displayed if user is not browsing with Tor."
    )
    subtitle = models.CharField(
        max_length=255,
        default="Your security is compromised while using this browser.",
        blank=True,
        null=True,
    )
    body = RichTextField(
        blank=True,
        null=True,
        help_text="Text explaining how and why to use Tor browser. Only displayed if user is not browsing with Tor."
    )
    tor_settings_title = models.CharField(
        max_length=255,
        default="Your Tor security settings are too low.",
        help_text="This alert is only displayed if the user is browsing with Tor already.")
    tor_settings_subtitle = models.CharField(
        max_length=255,
        default="These settings allow JavaScript to run which compromises your security.",
        blank=True,
        null=True,
    )
    tor_settings_body = RichTextField(
        blank=True,
        null=True,
        help_text="Text explaining how and why to change Tor security settings."
    )

    mobile_title = models.CharField(
        max_length=255,
        blank=True,
        help_text='Title of alert box displayed to users of mobile browsers',
    )
    mobile_subtitle = models.CharField(
        max_length=255,
        blank=True,
        help_text='Subtitle of alert box displayed to users of mobile browsers',
    )
    mobile_body = RichTextField(
        blank=True,
        help_text='Body text for the alert box displayed to users of mobile browsers',
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('title'),
                FieldPanel('subtitle'),
                FieldPanel('body'),
            ],
            "Tor Not Detected Alert",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('tor_settings_title'),
                FieldPanel('tor_settings_subtitle'),
                FieldPanel('tor_settings_body'),
            ],
            "Tor Settings Too Low Alert",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('mobile_title'),
                FieldPanel('mobile_subtitle'),
                FieldPanel('mobile_body'),
            ],
            'Tor Mobile Alert',
            classname='collapsible',
        ),
    ]


@register_setting(icon='plus')
class SocialSharingSEOSettings(BaseSiteSetting):
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
        FieldPanel('default_image'),
        FieldPanel('facebook_page_id'),
        FieldPanel('twitter'),
    ]

    class Meta:
        verbose_name = 'Social Sharing/SEO'


@register_setting(icon='password')
class TwoFactorAuthSettings(BaseSiteSetting):
    signup_form_text = RichTextField(
        blank=True,
        null=True,
        help_text='Message displayed on the signup page',
        default='Note: two-factor authentication is required to use your account.  After you complete this form, you must also complete setup of a two-factor authentication device.',
    )

    authenticate_text = RichTextField(
        blank=True,
        null=True,
        help_text='Message displayed on the 2FA authentication form, where the user must enter their token',
    )

    setup_text = RichTextField(
        blank=True,
        null=True,
        help_text='Message displayed on the 2FA setup form',
    )

    backup_tokens_text = RichTextField(
        blank=True,
        null=True,
        help_text='Message displayed on the 2FA backup tokens generation form',
    )

    remove_text = RichTextField(
        blank=True,
        null=True,
        help_text='Message displayed on the 2FA removal form',
    )
