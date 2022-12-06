from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel, FieldRowPanel,
    InlinePanel, MultiFieldPanel
)
from wagtail.fields import RichTextField
from wagtail.contrib.forms.models import AbstractFormField, AbstractEmailForm
from wagtail.images.edit_handlers import ImageChooserPanel

from common.models import MetadataPageMixin
from forms.utils import send_mail


class FormField(AbstractFormField):
    page = ParentalKey('FormPage', related_name='form_fields')

    image = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    image_caption = RichTextField(blank=True, null=True)
    image_link_text = models.CharField(
        blank=True,
        null=True,
        default='Show Image',
        max_length=50
    )
    show_image_thumbnail = models.BooleanField(default=False)

    panels = AbstractFormField.panels + [
        ImageChooserPanel('image'),
        FieldPanel('image_caption'),
        FieldPanel('image_link_text'),
        FieldPanel('show_image_thumbnail'),
    ]


@method_decorator(cache_control(private=True), name='serve')
class FormPage(MetadataPageMixin, AbstractEmailForm):
    intro = RichTextField(blank=True)
    warning = RichTextField(blank=True, help_text='A warning for sources not to submit documents via this form.')
    thank_you_text = RichTextField(blank=True)
    button_text = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )

    content_panels = AbstractEmailForm.content_panels + [
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

    def send_mail(self, form):
        """
        A modified clone of AbstractEmailForm.send_mail, which uses our own
        send_mail function to avoid including an
        'Auto-Submitted: auto-generated' header

        See forms.utils.send_mail for details
        """

        addresses = [x.strip() for x in self.to_address.split(',')]
        content = []
        for field in form:
            value = field.value()
            if isinstance(value, list):
                value = ', '.join(value)
            content.append('{}: {}'.format(field.label, value))
        content = '\n'.join(content)
        send_mail(self.subject, content, addresses, self.from_address,)
