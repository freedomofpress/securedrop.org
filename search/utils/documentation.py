from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from search.models import SearchDocument


READTHEDOCS_BASE = 'https://docs.securedrop.org/en/stable/'


def fetch_indexable_pages():
    """Fetch documentation root and extract a list of URLs to scrape"""
    url = urljoin(READTHEDOCS_BASE, 'index.html')
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Select the main nav bar and extract links from it
    nav = soup.select('div[aria-label="main navigation"]')[0]
    links = nav.find_all('a', href=True)
    return [urljoin(READTHEDOCS_BASE, link.get('href')) for link in links] + [url]


def scrape_documentation_page(url):
    """Fetch the contents from a URL for a documentation page"""
    return requests.get(url)


def index_documentation_page(url, page):
    """Parse a documentation page and update a search document for it"""
    soup = BeautifulSoup(page.content, 'html.parser')

    try:
        search_content = ''.join(soup.select('div[role=main]')[0].strings)
    except IndexError:
        search_content = ''
    if soup.title:
        title = soup.title.string
    else:
        title = url

    result = SearchDocument.objects.update_or_create(
        {
            'title': title,
            'url': url,
            'search_content': search_content,
            'data': {},
            'result_type': 'D',
        },
        key=url,
    )
    return result


def index_documentation_pages():
    """Create search documents for all indexable ReadTheDocs documentation pages"""
    for url in fetch_indexable_pages():
        page = scrape_documentation_page(url)
        index_documentation_page(url, page)
