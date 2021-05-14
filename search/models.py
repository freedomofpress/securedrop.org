from django.contrib.postgres.fields import HStoreField
from django.contrib.postgres.search import SearchVectorField

from django.db import models

from django.contrib.postgres.indexes import GinIndex


class SearchDocument(models.Model):
    RESULT_TYPES = (
        ('D', 'Documentation'),
        ('W', 'Wagtail Page')
    )

    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    search_content = models.TextField()
    data = HStoreField()
    result_type = models.CharField(max_length=1, choices=RESULT_TYPES)
    key = models.CharField(max_length=255, unique=True)
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector'])
        ]
