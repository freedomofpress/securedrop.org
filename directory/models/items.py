from django.db import models
from modelcluster.models import ClusterableModel


class BaseItem(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.title


class Language(BaseItem):
    pass


class Country(BaseItem):
    pass


class Topic(BaseItem):
    pass
