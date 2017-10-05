from django.db import models
from django.core.exceptions import ValidationError

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Orderable
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailsnippets.models import register_snippet


@register_snippet
class ResultGroup(ClusterableModel):
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
    name = models.CharField(
        max_length=255,
        help_text="Must be a field in the landing_page_checker.Result model."
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
