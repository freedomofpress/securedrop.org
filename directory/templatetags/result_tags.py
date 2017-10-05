from django import template
from directory.models import ResultGroup

register = template.Library()


@register.inclusion_tag('directory/tags/_result_groups.html', takes_context=True)
def result_groups(context, result, show_fixes):
    return {
        'result_groups': ResultGroup.objects.all(),
        'request': context['request'],
        'result': result,
        'show_fixes': show_fixes,
    }
