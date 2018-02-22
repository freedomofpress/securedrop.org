import datetime
from django.forms.utils import pretty_name
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.edit_handlers import EditHandler


class BaseReadOnlyPanel(EditHandler):
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
            'label': self.label,
            'value': self.get_value(),
        }))

    def render_as_field(self):
        template = "common/edit_handlers/read_only_field.html"
        return mark_safe(render_to_string(template, {  # nosec
            'label': self.label,
            'value': self.get_value(),
        }))


class ReadOnlyPanel:
    def __init__(self, attr, label=None, classname=''):
        self.attr = attr
        self.label = pretty_name(self.attr) if label is None else label
        self.classname = classname

    def bind_to_model(self, model):
        return type(str(_('ReadOnlyPanel')), (BaseReadOnlyPanel,),
                    {'attr': self.attr, 'label': self.label,
                     'classname': self.classname})
