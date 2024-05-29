from collections import deque, namedtuple
import re
import urllib.parse

import requests
import tinycss2
from typing import List
from bs4 import BeautifulSoup

from scanner.utils import HEADERS
from scanner.utils import extract_strings, extract_urls


Asset = namedtuple('Asset', ['resource', 'kind', 'initiator'])


def extract_assets(soup: BeautifulSoup, site_url: str) -> List[Asset]:
    assets = []

    images = soup.find_all('img')
    for image in images:
        if 'src' in image.attrs:
            assets.append(
                Asset(
                    resource=image.attrs['src'],
                    kind='img-src',
                    initiator=site_url
                )
            )
        if 'srcset' in image.attrs:
            srcset = parse_srcset(image.attrs['srcset'])
            for url in srcset:
                assets.append(
                    Asset(
                        resource=url,
                        kind='img-srcset',
                        initiator=site_url
                    )
                )

    for video in soup.find_all('video'):
        if 'src' in video.attrs:
            assets.append(
                Asset(
                    resource=video.attrs['src'],
                    kind='video-src',
                    initiator=site_url,
                )
            )
        if 'poster' in video.attrs:
            assets.append(
                Asset(
                    resource=video.attrs['poster'],
                    kind='video-poster',
                    initiator=site_url,
                )
            )

    # scan all simple tags that only have resources referenced in the
    # "src" attribute.
    for tag_name in ('source', 'audio', 'embed'):
        for tag in soup.find_all(tag_name):
            if 'src' in tag.attrs:
                assets.append(
                    Asset(
                        resource=tag.attrs['src'],
                        kind='{}-src'.format(tag_name),
                        initiator=site_url
                    )
                )

    scripts = soup.find_all('script')
    for script in scripts:
        if 'src' in script.attrs:
            # externally loaded js
            assets.append(
                Asset(
                    resource=script.attrs['src'],
                    kind='script-src',
                    initiator=site_url,
                )
            )

            asset_text = fetch_asset(script.attrs['src'], site_url)
            # assets in content from external js
            for text in extract_strings(asset_text):
                for url in extract_urls(text):
                    assets.append(Asset(resource=url, kind='script-resource', initiator=script.attrs['src']))
        # js embedded in <script> tags
        else:
            for text in extract_strings(script.get_text()):
                for url in extract_urls(text):
                    assets.append(
                        Asset(resource=url, kind='script-embed', initiator=site_url)
                    )

    iframe_tags = soup.find_all('iframe')
    for tag in iframe_tags:
        if tag.has_attr('src'):
            assets.append(Asset(resource=tag.attrs['src'], kind='iframe-src', initiator=site_url))

    stylesheet_links = soup.find_all('link', rel='stylesheet')
    for link in stylesheet_links:
        if link.attrs.get('href'):
            asset_text = fetch_asset(link.attrs['href'], site_url)
            # assets in content from stylesheet link
            for url in urls_from_css(asset_text):
                assets.append(Asset(resource=url, kind='style-resource', initiator=link.attrs['href']))

            # stylesheet link
            assets.append(Asset(resource=link.attrs['href'], kind='style-href', initiator=site_url))

    # css embedded in <style> tags
    style_tags = soup.find_all('style')
    for tag in style_tags:
        for item in tag.contents:
            if isinstance(item, str):
                for url in urls_from_css(item):
                    assets.append(Asset(resource=url, kind='style-embed', initiator=site_url))

    # inline styles
    for tag in soup.select('[style]'):
        for url in urls_from_css_declarations(tag.attrs['style']):
            assets.append(Asset(resource=url, kind='style-resource-inline', initiator=site_url))

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
            elif getattr(token, 'type', '') == 'function' and token.lower_name == 'url':
                urls.append(token.arguments[0].value)
    return urls


def urls_from_css(css_text: str) -> List[str]:
    """Given CSS text, parse it and return all URLs found"""
    urls = []
    nodes = tinycss2.parse_stylesheet(css_text)
    for node in descendants(nodes):
        if getattr(node, 'type', '') == 'url':
            urls.append(node.value)
        elif getattr(node, 'type', '') == 'function' and node.lower_name == 'url':
            urls.append(node.arguments[0].value)
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


def fetch_asset(asset_url: str, site_url: str) -> str:
    site_url = urllib.parse.urlparse(site_url)
    asset_url = urllib.parse.urlparse(asset_url)

    if not asset_url.scheme:
        asset_url = asset_url._replace(scheme=site_url.scheme)
    if not asset_url.netloc:
        asset_url = asset_url._replace(netloc=site_url.netloc)

    # Note: headers include User-Agent which is required for correct
    # scanning.
    try:
        response = requests.get(asset_url.geturl(), headers=HEADERS, timeout=5)
    except requests.RequestException:
        return ''
    return response.text


def parse_srcset(srcset: str) -> List[str]:
    """Extract URLs from a srcset attribute"""
    srcset = srcset.strip()
    if not srcset:
        return []
    urls = []
    for source in srcset.split(','):
        stripped_source = source.strip()
        if ' ' in stripped_source:
            url, _ = re.split(r'\ +', source.strip(), maxsplit=1)
        else:
            url = stripped_source
        urls.append(url)
    return urls
