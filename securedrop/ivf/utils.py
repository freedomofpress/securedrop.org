from bs4 import BeautifulSoup
import json
import re
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
            soup = BeautifulSoup(page.content, "lxml")
        except:
            return {'no_cookies': None,
                    'safe_onion_address': None,
                    'no_cdn': None,
                    'no_redirect': None,
                    'expected_encoding': None,
                    'no_analytics': None,
                    'no_server_info': None,
                    'no_server_version': None,
                    'csp_origin_only': None,
                    'mime_sniffing_blocked': None,
                    'noopen_download': None,
                    'xss_protection': None,
                    'clickjacking_protection': None,
                    'good_cross_domain_policy': None,
                    'http_1_0_caching_disabled': None,
                    'expires_set': None,
                    'cache_control_set': None,
                    'cache_control_revalidate_set': None,
                    'cache_control_nocache_set': None,
                    'cache_control_notransform_set': None,
                    'cache_control_nostore_set': None,
                    'cache_control_private_set': None,
                    '200_ok': False}
        return {'no_cookies': validate_no_cookies(page),
                'safe_onion_address': validate_onion_address_not_in_href(soup),
                'no_cdn': validate_not_using_cdn(page),
                'no_redirect': validate_no_redirects(page),
                'expected_encoding': validate_encoding(page),
                'no_analytics': validate_not_using_analytics(page),
                'no_server_info': validate_server_software(page),
                'no_server_version': validate_server_version(page),
                'csp_origin_only': validate_csp(page),
                'mime_sniffing_blocked': validate_no_sniff(page),
                'noopen_download': validate_download_options(page),
                'xss_protection': validate_xss_protection(page),
                'clickjacking_protection': validate_clickjacking_protection(page),
                'good_cross_domain_policy': validate_cross_domain_policy(page),
                'http_1_0_caching_disabled': validate_pragma(page),
                'expires_set': validate_expires(page),
                'cache_control_set': validate_cache_control_set(page),
                'cache_control_revalidate_set': validate_cache_must_revalidate(page),
                'cache_control_nocache_set': validate_nocache(page),
                'cache_control_notransform_set': validate_notransform(page),
                'cache_control_nostore_set': validate_nostore(page),
                'cache_control_private_set': validate_private(page),
                '200_ok': validate_200_ok(page)}


def compute_grade(results):
    if (results['https'] == False or
        results['scraping']['no_cookies'] == False or
        results['scraping']['no_redirect'] == False or
        results['scraping']['200_ok'] == False or
        results['scraping']['no_analytics'] == False):
        return 'F'
    elif (results['subdomain'] == True or
          results['scraping']['no_cdn'] == False or
          results['scraping']['no_server_info'] == False or
          results['scraping']['no_server_version'] == False):
        return 'D'
    elif (results['scraping']['expected_encoding'] == False or
          results['scraping']['noopen_download'] == False or
          results['scraping']['cache_control_set'] == False or
          results['scraping']['csp_origin_only'] == False or
          results['scraping']['mime_sniffing_blocked'] == False or
          results['scraping']['xss_protection'] == False or
          results['scraping']['clickjacking_protection'] == False or
          results['scraping']['good_cross_domain_policy'] == False or
          results['scraping']['http_1_0_caching_disabled'] == False or
          results['scraping']['expires_set'] == False):
        return 'C'
    elif (results['scraping']['cache_control_revalidate_set'] == False or
          results['scraping']['cache_control_nocache_set'] == False or
          results['scraping']['cache_control_notransform_set'] == False or
          results['scraping']['cache_control_nostore_set'] == False or
          results['scraping']['cache_control_private_set'] == False):
        return 'B'
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
    if len(url.split('.')) > 2 and url.split('.')[0] != 'www':
        return True
    else:
        return False


def validate_not_using_cdn(page):
    """Right now this is just checking for Cloudflare"""
    if 'CF-Cache-Status' in page.headers or 'CF-RAY' in page.headers:
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


def validate_security_header(page, header, expected_value):
    if header not in page.headers:
        return False
    elif page.headers[header] == expected_value:
        return True
    else:
        return False


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


def validate_server_software(page):
    if 'Server' not in page.headers:
        return True
    elif 'nginx' in page.headers['Server'] or 'apache' in page.headers['Server']:
        return False
    else:
        return True


def validate_server_version(page):
    version_regex = re.compile(r'\d+.\d+')

    if 'Server' not in page.headers:
        return True
    else:
        matches = version_regex.search(page.headers['Server'])

    if not matches:
        return True
    elif len(matches.group()) > 1:
        return False
    else:
        return True


def validate_csp(page):
    return validate_security_header(page,
                             "Content-Security-Policy",
                             "default-src 'self'")


def validate_xss_protection(page):
    return validate_security_header(page,
                             "X-XSS-Protection",
                             "1; mode=block")


def validate_no_sniff(page):
    return validate_security_header(page,
                             "X-Content-Type-Options",
                             "nosniff")


def validate_download_options(page):
    return validate_security_header(page,
                             "X-Download-Options",
                             "noopen")


def validate_clickjacking_protection(page):
    return validate_security_header(page,
                             "X-Frame-Options",
                             "DENY")


def validate_cross_domain_policy(page):
    return validate_security_header(page,
                             "X-Permitted-Cross-Domain-Policies",
                             "master-only")


def validate_pragma(page):
    return validate_security_header(page, "Pragma", "no-cache")


def validate_expires(page):
    return validate_security_header(page, "Expires", "-1")


def validate_cache_control_set(page):
    if 'Cache-Control' in page.headers:
        return True
    else:
        return False


def validate_cache_must_revalidate(page):
    return validate_security_header(page, "Cache-Control", "must-revalidate")


def validate_nocache(page):
    return validate_security_header(page, "Cache-Control", "no-cache")


def validate_nostore(page):
    return validate_security_header(page, "Cache-Control", "no-store")


def validate_notransform(page):
    return validate_security_header(page, "Cache-Control", "no-transform")


def validate_private(page):
    return validate_security_header(page, "Cache-Control", "private")


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
            # This means there isn't an href in the link. That's fine.
            pass
    return True
