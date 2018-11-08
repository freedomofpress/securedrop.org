from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.blocks.stream_block import StreamValue
from django.utils.html import strip_tags

from search.utils.search_elements import SearchElements


class SearchContentException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return 'SearchContentException(%s)' % self


def get_search_content_by_fields(page, fields, get_child_search_content=False):
    search_elements = SearchElements()
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
            search_elements.append(new_content)
        else:
            message = 'You are attempting to search by {} which does not exist on {}'.format(field, type(page))
            raise SearchContentException(message=message)

    return search_elements
