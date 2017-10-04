from django.contrib.postgres.fields import HStoreField
from django.db import models

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
    key = models.CharField(max_length=255)