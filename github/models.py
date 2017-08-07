from django.db import models


class Release(models.Model):
    url = models.URLField(blank=False, null=False)
    tag_name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )
    date = models.DateTimeField(blank=False, null=False)

    def __str__(self):
        return '{} released at {} ({})'.format(
            self.tag_name,
            self.date,
            self.url,
        )
