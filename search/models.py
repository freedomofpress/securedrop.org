from django.contrib.postgres.fields import HStoreField
from django.contrib.postgres.search import SearchVectorField, SearchVector

from django.db import models

from django.contrib.postgres.indexes import GinIndex


class SearchDocument(models.Model):
    RESULT_TYPES = (
        ('F', 'Forum'),
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

    def save(self, *args, **kwargs):
        """
        Update the search vector every time we save. We need to make sure to
        save the instance first before attempting to update the vector
        """
        super(SearchDocument, self).save(*args, **kwargs)
        if 'update_fields' not in kwargs or 'search_vector' not in kwargs['update_fields']:
            instance = self._meta.default_manager.get(pk=self.pk)
            instance.search_vector = SearchVector('title', 'search_content')
            instance.save(update_fields=['search_vector'])
