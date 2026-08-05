from typing import TYPE_CHECKING

from django import template


if TYPE_CHECKING:
    from django.forms.fields import Field
    from django.template.context import Context

register = template.Library()


@register.simple_tag(takes_context=True)
def field_extras(context: Context, form_field: Field):
    """
    Get FormField model instance for a Field

    Requires a Page object be in context with a FormField model
    manager at page.form_fields. Will search this manager for a FormField with
    the same name as the passed in Field
    """
    try:
        field_obj = filter(
            lambda mfield: form_field.name == mfield.clean_name,
            context["page"].form_fields.all(),
        ).__next__()
    except StopIteration:
        raise ValueError(f"Form field {form_field.name} not found in form")
    return field_obj


@register.simple_tag
def widget_type(field: Field) -> str:
    """
    Accepts a form field subclass and return a string value appropriate for a
    CSS class.
    """
    return type(field.widget).__name__.lower()
