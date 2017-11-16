from search.models import SearchDocument


KEY_FORMAT = 'wagtail-page-{}'


def index_wagtail_page(page):
    """
    Create or update a search document for a Wagtail Page. Returns an
    (object, created) tuple, where object is the created or updated object and
    created is a boolean specifying whether a new object was created.

    """

    # Make sure we have the most specific page subclass instance
    page = page.specific

    # We can't index the root page
    if page.is_root():
        return

    # We can't index non-routable pages
    if page.full_url is None:
        return

    # Get search content from page instance
    search_content = page.get_search_content() if hasattr(page, 'get_search_content') else ''

    # Create a new SearchDocument
    document_key = KEY_FORMAT.format(page.pk)
    result = SearchDocument.objects.update_or_create(
        {
            'title': page.title,
            'url': page.full_url,
            'search_content': search_content,
            'data': {},
            'result_type': 'W',
            'key': document_key,
        },
        key=document_key
    )

    return result


def index_wagtail_pages(queryset):
    """
    Create or update search documents for multiple Wagtail Pages. Returns a list
    of (object, created) tuples, where object is the created or updated object
    and created is a boolean specifying whether a new object was created.

    """

    # Make sure we get only live, non-root pages in their most specific
    # subclass instance
    pages = queryset.filter(depth__gt=1).live().specific()

    results = []
    for page in pages:
        results.append(index_wagtail_page(page))

    return results


def delete_wagtail_page(page):
    """
    Delete search document for a single Wagtail Page

    """

    key = KEY_FORMAT.format(page.pk)
    try:
        SearchDocument.objects.get(key=key).delete()
    except SearchDocument.DoesNotExist:
        # Don't bother deleting if it doesn't exist
        pass
