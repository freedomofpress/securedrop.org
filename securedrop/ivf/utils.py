from bs4 import BeautifulSoup
import json
import requests


class LandingPage(object):
    def __init__(self, url):
        self.url = url

    def get_results(self):
        scraping_results = self.request_and_scrape_page()
        https_results = ''
        results = {'https': validate_https(self.url),
                   'subdomain': validate_subdomain(self.url),
                   'scraping': scraping_results}
        grade = compute_grade(results)
        return results, grade

    def request_and_scrape_page(self):
        try:
            page = requests.get(self.url)
            soup = BeautifulSoup(page.content)
        except:
            return {'no_cookies': None,
                    'safe_onion_address': None,
                    'cache_headers': None,
                    'no_cdn': None,
                    'no_redirect': None,
                    'expected_encoding': None,
                    'no_analytics': None,
                    'no_server_info': None,
                    '200_ok': False}
        return {'no_cookies': validate_no_cookies(page),
                'safe_onion_address': validate_onion_address_not_in_href(soup),
                'cache_headers': validate_cache_headers(page),
                'no_cdn': validate_not_using_cdn(page),
                'no_redirect': validate_no_redirects(page),
                'expected_encoding': validate_encoding(page),
                'no_analytics': validate_not_using_analytics(page),
                'no_server_info': validate_server_header(page),
                '200_ok': validate_200_ok(page)}


def compute_grade(results):
    if (results['https'] == False or
        results['scraping']['no_cookies'] == False or
        results['scraping']['no_redirect'] == False or
        results['scraping']['200_ok'] == False or
        results['scraping']['no_analytics'] == False or
        results['scraping']['no_server_info'] == False):
        return 'F'
    elif (results['subdomain'] == True or
          results['scraping']['no_cdn'] == False):
        return 'D'
    elif results['scraping']['expected_encoding'] == False:
        return 'C'
    else:
        return 'A'


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


def validate_not_using_cdn(page):
    """Right now this is just checking for Cloudflare"""
    if 'CF-Cache-Status' in page.headers:
        return False
    else:
        return True


def validate_not_using_analytics(page):
    """Right now this is just checking for Google Analytics

    Documentation: https://support.google.com/analytics/answer/1032399?hl=en
    """
    if 'analytics.js' in str(page.content) or 'ga.js' in str(page.content):
        return False
    else:
        return True


def validate_no_redirects(page):
    if page.is_redirect:
        return False
    else:
        return True


def validate_200_ok(page):
    if page.status_code == 200:
        return True
    else:
        return False


def validate_encoding(page):
    if page.encoding.upper() in ('UTF-8', 'ISO-8859-1'):
        return True
    else:
        return False


def validate_server_header(page):
    if 'Server' not in page.headers:
        return True
    elif 'nginx' in page.headers['Server'] or 'apache' in page.headers['Server']:
        return False
    else:
        return True


def validate_cache_headers(url):

    return {''}


def validate_no_cookies(page):
    if len(page.cookies.keys()) > 0:
        return False
    else:
        return True


def validate_onion_address_not_in_href(page):
    links_on_landing_page = page.find_all("a")
    for link in links_on_landing_page:
        try:
            if '.onion' in link.attrs['href']:
                return False
        except KeyError:
            # This means there isn't an href. That's fine.
            pass
    return True
