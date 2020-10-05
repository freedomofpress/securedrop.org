from django.core.validators import RegexValidator, URLValidator
from django.db import models

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel


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
    donation_url = models.URLField()
    contribute_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    securedrop_onion_address = models.CharField(
        'SecureDrop Onion Address',
        max_length=255,
        default='http://secrdrop5wyphb5x.onion',
        validators=[
            RegexValidator(regex=r'\.onion$', message="Enter a valid .onion address."),
            URLValidator(schemes=['http', 'https'], message='Onion address must be a valid URL beginning with http or https'),
        ],
        help_text='Address for the securedrop.org onion service. Displayed in the site footer and the Onion-Location header.  Must begin with http or https and end with .onion',
    )

    panels = [
        FieldPanel('title'),
        SnippetChooserPanel('main_menu'),
        FieldPanel('donation_url'),
        PageChooserPanel('contribute_link'),
        FieldPanel('securedrop_onion_address'),
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


@register_setting(icon='warning')
class TorAlertSettings(BaseSetting):
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


@register_setting(icon='password')
class TwoFactorAuthSettings(BaseSetting):
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
