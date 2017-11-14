from bs4 import BeautifulSoup
import json
import requests
import re
import subprocess

from django.utils import timezone

from landing_page_checker.models import Result


def clean_url(url):
    if len(url.split('//')) > 1:
        return url.split('//')[1]
    else:
        return url


def scan(securedrop):
    """Scan a single site"""

    try:
        pshtt_results = pshtt(securedrop.landing_page_domain)
    except:
        return Result(
            securedrop=securedrop,
            live=pshtt_results['Live'],
            http_status_200_ok=False,
        )

    try:
        page, soup = request_and_scrape_page(securedrop.landing_page_domain)

        # In order to check the HTTP status code and redirect status, we must
        # pass
        no_redirects_page, _ = request_and_scrape_page(
            securedrop.landing_page_domain, allow_redirects=False
        )
    except requests.exceptions.RequestException:
        # Connection timed out, an invalid HTTP response was returned, or
        # a network problem occurred.
        # Catch the base class exception for these cases.
        return Result(
            securedrop=securedrop,
            live=pshtt_results['Live'],
            http_status_200_ok=False,
        )

    return Result(
        securedrop=securedrop,
        live=pshtt_results['Live'],
        http_status_200_ok=validate_200_ok(no_redirects_page),
        forces_https=pshtt_results['Strictly Forces HTTPS'],
        hsts=pshtt_results['HSTS'],
        hsts_max_age=validate_hsts_max_age(pshtt_results['HSTS Max Age']),
        hsts_entire_domain=validate_hsts_entire_domain(pshtt_results['HSTS Entire Domain']),
        hsts_preloaded=pshtt_results['HSTS Preloaded'],
        subdomain=validate_subdomain(securedrop.landing_page_domain),
        no_cookies=validate_no_cookies(page),
        safe_onion_address=validate_onion_address_not_in_href(soup),
        no_cdn=validate_not_using_cdn(page),
        http_no_redirect=validate_no_redirects(no_redirects_page),
        expected_encoding=validate_encoding(page),
        no_analytics=validate_not_using_analytics(page),
        no_server_info=validate_server_software(page),
        no_server_version=validate_server_version(page),
        csp_origin_only=validate_csp(page),
        mime_sniffing_blocked=validate_no_sniff(page),
        noopen_download=validate_download_options(page),
        xss_protection=validate_xss_protection(page),
        clickjacking_protection=validate_clickjacking_protection(page),
        good_cross_domain_policy=validate_cross_domain_policy(page),
        http_1_0_caching_disabled=validate_pragma(page),
        expires_set=validate_expires(page),
        cache_control_set=validate_cache_control_set(page),
        cache_control_revalidate_set=validate_cache_must_revalidate(page),
        cache_control_nocache_set=validate_nocache(page),
        cache_control_notransform_set=validate_notransform(page),
        cache_control_nostore_set=validate_nostore(page),
        cache_control_private_set=validate_private(page),
    )


def bulk_scan(securedrops):
    for securedrop in securedrops:
        current_result = scan(securedrop)

        # Before we save, let's get the most recent scan before saving
        try:
            prior_result = securedrop.results.latest()
        except Result.DoesNotExist:
            current_result.save()
            continue

        if prior_result.is_equal_to(current_result):
            # Then let's not waste a row in the database
            prior_result.result_last_seen = timezone.now()
            prior_result.save()
        else:
            # Then let's add this new scan result to the database
            current_result.save()


def pshtt(url):
    # Function adapted from Secure The News https://securethe.news
    domain = clean_url(url).split('/')[0]

    pshtt_cmd = ['pshtt', '--json', '--timeout', '10', domain]

    p = subprocess.Popen(
        pshtt_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)
    stdout, stderr = p.communicate()

    try:
        pshtt_results = json.loads(stdout)[0]
    except ValueError:
        pshtt_results = {}
        pshtt_results['Live'] = False

    return pshtt_results


def request_and_scrape_page(domain, allow_redirects=True):
    try:
        page = requests.get(domain, allow_redirects=allow_redirects)
        soup = BeautifulSoup(page.content, "lxml")
    except requests.exceptions.MissingSchema:
        page = requests.get('https://{}'.format(domain), allow_redirects=allow_redirects)
        soup = BeautifulSoup(page.content, "lxml")

    return page, soup


def validate_subdomain(url):
    """Is the landing page on a subdomain"""
    if len(url.split('.')) > 2 and url.split('.')[0] != 'https://www':
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


def validate_hsts_max_age(max_age):
    if max_age and max_age >= 16070400:
        return True
    else:
        return False


def validate_hsts_entire_domain(pshtt_result):
    # Ensures a boolean response for proper template rendering
    if pshtt_result:
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
    else:
        server_header = str.lower(page.headers['Server'])
    if 'nginx' in server_header or 'apache' in server_header:
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
    if 'Content-Security-Policy' not in page.headers:
        return False
    elif "default-src 'self'" not in page.headers['Content-Security-Policy']:
        return False
    else:
        return True


def validate_xss_protection(page):
    return validate_security_header(
        page,
        "X-XSS-Protection",
        "1; mode=block",
    )


def validate_no_sniff(page):
    return validate_security_header(
        page,
        "X-Content-Type-Options",
        "nosniff",
    )


def validate_download_options(page):
    return validate_security_header(
        page,
        "X-Download-Options",
        "noopen",
    )


def validate_clickjacking_protection(page):
    return validate_security_header(
        page,
        "X-Frame-Options",
        "DENY",
    )


def validate_cross_domain_policy(page):
    return validate_security_header(
        page,
        "X-Permitted-Cross-Domain-Policies",
        "master-only",
    )


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
