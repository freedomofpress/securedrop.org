from django.db import models
from wagtail.wagtailimages.models import Image, AbstractImage, AbstractRendition


class CustomImage(AbstractImage):
    attribution = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Organization/Photographer. Image description can be set via the caption.'
    )

    admin_form_fields = Image.admin_form_fields + (
        'attribution',
    )


class CustomRendition(AbstractRendition):
    """This class is required by Wagtail when using a custom image.
    """

    image = models.ForeignKey(CustomImage, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )
