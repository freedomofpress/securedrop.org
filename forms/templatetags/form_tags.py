from functools import partial
from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from django.forms.fields import Field  # NOQA: F401
    from django.template.context import Context  # NOQA: F401

register = template.Library()


@register.simple_tag(takes_context=True)
def field_extras(context: 'Context', form_field: 'Field'):
    """
    Get FormField model instance for a Field

    Requires a Page object be in context with a FormField model
    manager at page.form_fields. Will search this manager for a FormField with
    the same name as the passed in Field
    """
    field_obj = filter(
        partial(
            lambda ffield, mfield: ffield.name == mfield.clean_name,
            form_field
        ),
        context['page'].form_fields.all()
    ).__next__()
    return field_obj
