from bs4 import BeautifulSoup
import json
import requests


def get_results(url):
    scraping_results = scrape_page(url)
    https_results = ''
    return {'https': validate_https(url),
            'subdomain': validate_subdomain(url),
            'scraping': scraping_results}


def scrape_page(url):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content)
    except:
        return {'scraping': 'null'}
    return {'no_cookies': validate_no_cookies(page),
            'safe_onion_address': validate_securedrop_onion_address_not_in_href(soup)}


def validate_https(url):
    """Is the string 'https' in the URL?"""
    if 'https' not in url:
        return False
    elif 'https' in url:
        return True


def validate_subdomain(url):
    """Is the landing page on a subdomain"""
    if len(url.split('.')) > 2:
        return True
    else:
        return False


def validate_no_cookies(page):
    if len(page.cookies.keys()) > 0:
        return False
    else:
        return True


def validate_securedrop_onion_address_not_in_href(page):
    links_on_landing_page = page.find_all("a")
    for link in links_on_landing_page:
        if '.onion' in link.attrs['href']:
            return False
    return True
