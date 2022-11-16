from django.contrib.auth.models import Group
from django.db import models

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel
from wagtail.fields import RichTextField
from wagtail.documents.edit_handlers import DocumentChooserPanel


@register_setting(icon='form')
class DirectorySettings(BaseSetting):

    # Contact
    new_instance_alert_group = models.OneToOneField(
        Group,
        blank=True,
        null=True,
        help_text='Users in this group will get an email alert when a new SecureDrop instance is submitted',
        on_delete=models.CASCADE,
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
    report_error_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Report Error Page',
        help_text='Form for submitting Error Reports'
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
            FieldPanel('show_scan_results'),
        ], 'Feature Flags'),
        MultiFieldPanel([
            FieldPanel('new_instance_alert_group'),
            FieldPanel('contact_email'),
            PageChooserPanel('report_error_page', 'forms.FormPage'),
            DocumentChooserPanel('contact_gpg'),
        ], 'Contact'),
    ]

    class Meta:
        verbose_name = 'Directory Settings'
