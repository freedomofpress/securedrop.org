from django.db import models


class Button(models.Model):
    text = models.CharField(max_length=50)
    link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
