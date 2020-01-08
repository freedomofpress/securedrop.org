import datetime
from django.forms.utils import pretty_name
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from wagtail.admin.edit_handlers import EditHandler


class ReadOnlyPanel(EditHandler):
    def __init__(self, attr, *args, **kwargs):
        self.attr = attr
        if 'heading' not in kwargs:
            kwargs['heading'] = pretty_name(self.attr)
        super().__init__(*args, **kwargs)

    def clone(self):
        return self.__class__(
            attr=self.attr,
            heading=self.heading,
            classname=self.classname,
            help_text=self.help_text,
        )

    def get_value(self):
        value = getattr(self.instance, self.attr)
        if isinstance(value, datetime.date):
            value = value.strftime('%A, %B %d, %Y %X')
        if callable(value):
            value = value()
        return value

    def render_as_object(self):
        template = "common/edit_handlers/read_only_object.html"
        return mark_safe(render_to_string(template, {  # nosec
            'heading': self.heading,
            'value': self.get_value(),
        }))

    def render_as_field(self):
        template = "common/edit_handlers/read_only_field.html"
        return mark_safe(render_to_string(template, {  # nosec
            'heading': self.heading,
            'value': self.get_value(),
        }))
