import bleach
from django import template
from django.urls import reverse
from django.utils.html import mark_safe
from wagtail.core.templatetags.wagtailcore_tags import richtext
from wagtail.core.models import Site

register = template.Library()


@register.filter
def first_block_of(blocks, type):
    for block in blocks:
        if block.block_type == type:
            return block


@register.filter
def richtext_inline(value):
    "Returns HTML-formatted rich text stripped of block level elements"
    text = richtext(value)
    return mark_safe(bleach.clean(
        text,
        strip=True,
        tags=[
            'a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong', 'span'
        ]
    ))


@register.filter
def richtext_isempty(value):
    """
    Returns True if a value is an empty string, none, or a string containing
    nothing but paragraph tags

    This is a workaround for a resolution to
    https://github.com/wagtail/wagtail/issues/4549
    """

    return any([
        value is None,
        value == '',
        value == '<p></p>',
    ])


@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return updated.urlencode()


@register.filter
def get_attr(obj, attribute):
    """ Try to get an attribute from an object

    Returns false if object does not exist
    """
    if hasattr(obj, attribute):
        return getattr(obj, attribute)
    return False


@register.simple_tag
def get_site_name():
    return Site.objects.get(is_default_site=True).site_name


@register.filter
def document_view_url(value):
    return reverse('view_document', args=[value.id, value.filename])
