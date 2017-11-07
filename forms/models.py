from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel
)
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailforms.models import AbstractFormField
from wagtailcaptcha.models import WagtailCaptchaEmailForm

from common.models import MetadataPageMixin


class FormField(AbstractFormField):
    page = ParentalKey('FormPage', related_name='form_fields')


class FormPage(MetadataPageMixin, WagtailCaptchaEmailForm):
    intro = RichTextField(blank=True)
    warning = RichTextField(blank=True, help_text='A warning for sources not to submit documents via this form.')
    thank_you_text = RichTextField(blank=True)
    button_text = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )

    content_panels = WagtailCaptchaEmailForm.content_panels + [
        FieldPanel('intro', classname="full"),
        FieldPanel('warning', classname="full"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        FieldPanel('button_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]
