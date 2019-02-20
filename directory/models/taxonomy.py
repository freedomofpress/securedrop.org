from django.db import models

from modelcluster.models import ClusterableModel

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.snippets.models import register_snippet


class AbstractBaseItem(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
    )

    order_priority = models.IntegerField(
        default=0,
        help_text=(
            'Default ordering will be by title. Use this field if certain '
            'items should always be at then top or bottom of lists (larger '
            'number is closer to top)'
        )
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('order_priority'),
    ]

    class Meta:
        abstract = True
        ordering = ['-order_priority', 'title']
        indexes = [
            models.Index(fields=['-order_priority', 'title']),
        ]

    def __str__(self):
        return self.title


@register_snippet
class Language(AbstractBaseItem):
    pass


@register_snippet
class Country(AbstractBaseItem):
    pass

    class Meta(AbstractBaseItem.Meta):
        verbose_name_plural = 'Countries'


@register_snippet
class Topic(AbstractBaseItem):
    pass
