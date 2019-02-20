from django.db import models
from wagtail.images.models import Image, AbstractImage, AbstractRendition


class CustomImage(AbstractImage):
    attribution = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Organization/Photographer.'
    )

    admin_form_fields = Image.admin_form_fields + (
        'attribution',
    )


class CustomRendition(AbstractRendition):
    """This class is required by Wagtail when using a custom image.
    """

    image = models.ForeignKey(CustomImage, related_name='renditions', on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )
