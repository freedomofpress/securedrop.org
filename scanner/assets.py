from collections import deque, namedtuple
import urllib.parse

import requests
import tinycss2
from typing import List
from bs4 import BeautifulSoup

from scanner.utils import extract_strings, extract_urls


Asset = namedtuple('Asset', ['url', 'source'])


def extract_assets(soup: BeautifulSoup, url: str) -> List[Asset]:
    site_url = urllib.parse.urlparse(url)
    assets = []

    images = soup.find_all('img')
    for image in images:
        if 'src' in image.attrs:
            assets.append(Asset(url=image.attrs['src'], source='image'))

    scripts = soup.find_all('script')
    for script in scripts:
        if 'src' in script.attrs:
            assets.append(Asset(url=script.attrs['src'], source='external-js'))
        else:
            for text in extract_strings(script.get_text()):
                for url in extract_urls(text):
                    assets.append(Asset(url=url, source='embedded-js'))

    iframe_tags = soup.find_all('iframe')
    for tag in iframe_tags:
        if tag.has_attr('src'):
            assets.append(Asset(url=tag.attrs['src'], source='iframe'))

    stylesheet_links = soup.find_all('link', rel='stylesheet')
    for link in stylesheet_links:
        if link.attrs.get('href'):
            link_target = urllib.parse.urlparse(link.attrs['href'])
            if not link_target.scheme:
                link_target = link_target._replace(scheme=site_url.scheme)
            if not link_target.netloc:
                link_target = link_target._replace(netloc=site_url.netloc)

            response = requests.get(link_target.geturl())
            for url in urls_from_css(response.text):
                assets.append(Asset(url=url, source='css-link'))

            assets.append(Asset(url=link.attrs['href'], source='css-link'))

    style_tags = soup.find_all('style')
    for tag in style_tags:
        for item in tag.contents:
            if isinstance(item, str):
                for url in urls_from_css(item):
                    assets.append(Asset(url=url, source='css-embedded'))

    for tag in soup.select('[style]'):
        for url in urls_from_css_declarations(tag.attrs['style']):
            assets.append(Asset(url=url, source='css-inline'))

    return assets


def urls_from_css_declarations(css_text: str) -> List[str]:
    """Parse text consisting of one or more CSS declarations and return a
    list of urls found within.  The CSS text given should not include
    any selectors.

    """
    urls = []
    for declaration in tinycss2.parse_declaration_list(css_text):
        for token in declaration.value:
            if getattr(token, 'type', '') == 'url':
                urls.append(token.value)
    return urls


def urls_from_css(css_text: str) -> List[str]:
    """Given CSS text, parse it and return all URLs found"""
    urls = []
    nodes = tinycss2.parse_stylesheet(css_text)
    for node in descendants(nodes):
        if getattr(node, 'type', '') == 'url':
            urls.append(node.value)
    return urls


def descendants(nodes):
    """Crawl a list of tinycss2-parsed nodes and return all descendants"""
    to_crawl = deque(nodes)
    children = []
    while to_crawl:
        current = to_crawl.popleft()
        children.append(current)
        prelude = getattr(current, 'prelude', [])
        if prelude:
            to_crawl.extend(prelude)
        content = getattr(current, 'content', [])
        if content:
            to_crawl.extend(content)
    return children
