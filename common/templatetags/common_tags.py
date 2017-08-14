import bleach
from django import template
from django.utils.html import mark_safe
from wagtail.wagtailcore.templatetags.wagtailcore_tags import richtext

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


@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    return updated.urlencode()
