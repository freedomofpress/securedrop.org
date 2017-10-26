from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


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
