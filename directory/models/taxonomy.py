from django.db import models
from modelcluster.models import ClusterableModel


class AbstractBaseItem(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(
        max_length=255,
        unique=True,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Language(AbstractBaseItem):
    pass


class Country(AbstractBaseItem):
    pass


class Topic(AbstractBaseItem):
    pass
