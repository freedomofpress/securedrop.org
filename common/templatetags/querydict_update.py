from django import template

register = template.Library()


@register.simple_tag
def querydict_update(qdict, **kwargs):
    new_qdict = qdict.copy()
    for k, v in kwargs.items():
        new_qdict[k] = v
    return new_qdict
