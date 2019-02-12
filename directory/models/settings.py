from django.contrib.auth.models import Group
from django.db import models

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.fields import RichTextField
from wagtail.documents.edit_handlers import DocumentChooserPanel


@register_setting(icon='form')
class DirectorySettings(BaseSetting):

    # Contact
    new_instance_alert_group = models.OneToOneField(
        Group,
        blank=True,
        null=True,
        help_text='Users in this group will get an email alert when a new SecureDrop instance is submitted',
    )
    contact_email = models.EmailField(
        default='securedrop@freedom.press',
        help_text='People should contact this email address about inaccuracies '
                  'or potential attacks in the directory'
    )
    contact_gpg = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Contact email GPG',
        help_text='Public key for email communication'
    )

    # Messages
    grade_text = models.CharField(
        max_length=100,
        default='Security Grade'
    )
    no_results_text = RichTextField(
        default='Results could not be calculated.',
        help_text='Text displayed when there are no results for a results group.'
    )

    # Feature flags
    allow_directory_management = models.BooleanField(
        default=False,
        help_text='Allow directory instance submission/management by '
                  'site visitors'
    )
    show_scan_results = models.BooleanField(
        default=False,
        help_text='Show directory instance scan results on public site'
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('grade_text'),
            FieldPanel('no_results_text'),
        ], 'Messages'),
        MultiFieldPanel([
            FieldPanel('allow_directory_management'),
            FieldPanel('show_scan_results'),
        ], 'Feature Flags'),
        MultiFieldPanel([
            FieldPanel('new_instance_alert_group'),
            FieldPanel('contact_email'),
            DocumentChooserPanel('contact_gpg'),
        ], 'Contact'),
    ]

    class Meta:
        verbose_name = 'Directory Settings'
