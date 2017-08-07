from django import template
from menus.models import MenuItem


register = template.Library()


@register.assignment_tag
def get_menu(slug):
    try:
        items = MenuItem.objects.filter(
            menu__slug=slug
        ).select_related(
            'link_page',
            'link_document',
        )
    except:  # Pokemon Exception Handling
        return None
    return items
