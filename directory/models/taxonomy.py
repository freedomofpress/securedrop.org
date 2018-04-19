from django.db import models

from modelcluster.models import ClusterableModel

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailsnippets.models import register_snippet


class AbstractBaseItem(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(
        max_length=255,
        unique=True,
    )

    panels = [
        FieldPanel('title'),
    ]

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


@register_snippet
class Language(AbstractBaseItem):
    pass


@register_snippet
class Country(AbstractBaseItem):
    pass

    class Meta:
        verbose_name_plural = 'Countries'


@register_snippet
class Topic(AbstractBaseItem):
    pass
