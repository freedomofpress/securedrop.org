import re

from typing import Set, List

WEB_URL_REGEX = re.compile(r"""\b((?:https?:\/\/)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:[\/\w\.-?]*)*\/?)""")


def url_to_domain(url: str) -> str:
    # Split off the protocol
    if len(url.split('//')) > 1:
        url = url.split('//')[1]
    # Split off any subpath
    url = url.split('/')[0]
    return url


def extract_strings(text: str) -> Set[str]:
    """Find unique quoted strings in a block of code"""
    return set(re.findall(r'["\'](.*?)["\']', text))


def extract_urls(text: str) -> List[str]:
    return WEB_URL_REGEX.findall(text)
