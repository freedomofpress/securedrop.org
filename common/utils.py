from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.blocks.stream_block import StreamValue
from django.utils.html import strip_tags

DEFAULT_PAGE_KEY = 'page'


def paginate(request, items, page_key=DEFAULT_PAGE_KEY, per_page=20, orphans=10):
    page = request.GET.get(page_key, 1)

    # See https://docs.djangoproject.com/en/1.10/topics/pagination/#using-paginator-in-a-view
    paginator = Paginator(items, per_page)
    try:
        page = paginator.page(page)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return paginator, page


def get_search_content_by_fields(page, fields, get_child_search_content=False):
    search_content = ''
    for field in fields:
        if hasattr(page, field):
            content = getattr(page, field)
            if content is None:
                pass
            elif isinstance(content, Page):
                child_page = content
                if hasattr(child_page.specific, 'get_search_content') and get_child_search_content:
                    new_content = child_page.specific.get_search_content()
                else:
                    new_content = child_page.title
            elif isinstance(content, StreamValue):
                new_content = strip_tags(content.__str__())
            elif isinstance(content, str):
                new_content = strip_tags(content)
            else:
                new_content = content.title
            search_content += new_content + ' '
    return search_content
