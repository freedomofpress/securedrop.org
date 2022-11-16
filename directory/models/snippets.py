from django.db import models

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from wagtail.models import Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.snippets.models import register_snippet


@register_snippet
class ResultGroup(ClusterableModel):
    """
    A model that defines how fields on ScanResults are organized when they are
    displayed
    """

    name = models.CharField(
        max_length=255,
        help_text="Will be displayed as the group heading."
    )

    panels = [
        FieldPanel('name'),
        InlinePanel('result_states', label='Result States')
    ]

    def __str__(self):
        return self.name


class ResultState(Orderable):
    """
    Represents a field on a ScanResult. Lets Wagtail admins define how
    success and failure states for those fields are displayed
    """
    name = models.CharField(
        max_length=255,
        help_text="Must be a field in the directory.ScanResult model."
    )
    result_group = ParentalKey(ResultGroup, related_name='result_states')
    success_text = RichTextField()
    failure_text = RichTextField()
    is_warning = models.BooleanField(help_text="If checked, will display a flag and yellow text. If left unchecked, will display an x and red text.")
    fix_text = RichTextField(blank=True, null=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('success_text'),
        FieldPanel('failure_text'),
        FieldPanel('is_warning'),
        FieldPanel('fix_text'),
    ]

    class Meta:
        indexes = [
            models.Index(fields=['result_group']),
            models.Index(fields=['sort_order']),
        ]
