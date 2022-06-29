from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from search.models import SearchDocument
from search.utils.search_elements import SearchElements


READTHEDOCS_BASE = 'https://docs.securedrop.org/en/stable/'


def fetch_indexable_pages():
    """Fetch documentation root and extract a list of URLs to scrape"""
    url = urljoin(READTHEDOCS_BASE, 'index.html')
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Select the main nav bar and extract links from it
    nav = soup.select('div[aria-label="Navigation menu"]')[0]
    links = nav.find_all('a', href=True)
    return [urljoin(READTHEDOCS_BASE, link.get('href')) for link in links] + [url]


def scrape_documentation_page(url):
    """Fetch the contents from a URL for a documentation page"""
    return requests.get(url)


def index_documentation_page(url, page):
    """Parse a documentation page and update a search document for it"""
    soup = BeautifulSoup(page.content, 'html.parser')

    search_elements = SearchElements()

    try:
        search_elements.append(''.join(soup.select('div[role=main]')[0].strings))
    except IndexError:
        search_elements.append('')
    if soup.title:
        title = soup.title.string
        search_elements.append(title)
    else:
        title = url

    result = SearchDocument.objects.update_or_create(
        {
            'title': title,
            'url': url,
            'search_content': search_elements.as_string(),
            'search_vector': search_elements.as_search_vector(),
            'data': {},
            'result_type': 'D',
        },
        key=url,
    )
    return result


def index_documentation_pages():
    """Create search documents for all indexable ReadTheDocs documentation pages"""
    results = []
    for url in fetch_indexable_pages():
        page = scrape_documentation_page(url)
        results.append(index_documentation_page(url, page))
    return results
