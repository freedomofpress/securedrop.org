from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from django.forms.fields import Field  # NOQA: F401


register = template.Library()


@register.filter
def widget_type(field: 'Field') -> str:
    """
    Accepts a form field subclass and return a string value appropriate for a
    CSS class.
    """
    return type(field.widget).__name__.lower()
