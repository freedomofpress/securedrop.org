from __future__ import absolute_import, unicode_literals

from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Func, F, TextField
from django.shortcuts import render
from wagtail.wagtailcore.models import Site

from search.models import SearchDocument


def search(request):
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search
    if search_query:
        vector = SearchVector('title', 'search_content')
        query = SearchQuery(search_query)
        search_results = SearchDocument.objects.annotate(
            rank=SearchRank(vector, query),
            search=vector,
            description=Func(F('search_content'), query, function='TS_HEADLINE', output_field=TextField())
        ).filter(
            search=query
        ).order_by('-rank')
    else:
        search_results = SearchDocument.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
        'site_name': Site.objects.get(is_default_site=True).site_name
    })
