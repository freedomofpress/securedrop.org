from bs4 import BeautifulSoup
import requests
import re

from typing import Dict, TYPE_CHECKING

from pshtt.pshtt import inspect_domains
import tldextract

from django.utils import timezone

from directory.models import ScanResult, DirectoryEntry
from scanner.utils import url_to_domain

if TYPE_CHECKING:
    from directory.models import DirectoryEntryQuerySet  # noqa: F401


def pshtt_data_to_result(securedrop: DirectoryEntry, pshtt_results: Dict) -> ScanResult:
    """
    Takes a DirectoryEntry and a dictionary of pshtt results for that domain,
    scans the page itself and then combines those results into an unsaved
    ScanResult object
    """
    try:
        page, soup = request_and_scrape_page(securedrop.landing_page_url)

        # In order to check the HTTP status code and redirect status, we must
        # pass
        no_redirects_page, _ = request_and_scrape_page(
            securedrop.landing_page_url, allow_redirects=False
        )
    except requests.exceptions.RequestException:
        # Connection timed out, an invalid HTTP response was returned, or
        # a network problem occurred.
        # Catch the base class exception for these cases.
        return ScanResult(
            securedrop=securedrop,
            live=pshtt_results['Live'],
            http_status_200_ok=False,
        )

    return ScanResult(
        landing_page_url=securedrop.landing_page_url,
        live=pshtt_results['Live'],
        http_status_200_ok=validate_200_ok(no_redirects_page),
        forces_https=bool(pshtt_results['Strictly Forces HTTPS']),
        hsts=pshtt_results['HSTS'],
        hsts_max_age=validate_hsts_max_age(pshtt_results['HSTS Max Age']),
        hsts_entire_domain=validate_hsts_entire_domain(pshtt_results['HSTS Entire Domain']),
        hsts_preloaded=pshtt_results['HSTS Preloaded'],
        subdomain=validate_subdomain(securedrop.landing_page_url),
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
        referrer_policy_set_to_no_referrer=validate_no_referrer_policy(page),
    )


def scan(securedrop: DirectoryEntry, commit=False) -> ScanResult:
    """
    Scan a single site. This method accepts a DirectoryEntry instance which
    may or may not be saved to the database. You can optionally pass True for
    the commit argument, which will save the result to the database. In that
    case, the passed DirectoryEntry *must* already be in the database.
    """

    securedrop_domain = url_to_domain(securedrop.landing_page_url)
    pshtt_results = inspect_domains([securedrop_domain], {'timeout': 10})
    result = pshtt_data_to_result(securedrop, pshtt_results[0])

    if commit:
        result.securedrop = securedrop
        result.save()

    return result


def bulk_scan(securedrops: 'DirectoryEntryQuerySet') -> None:
    """
    This method takes a queryset and scans the securedrop pages. Unlike the
    scan method that takes a single SecureDrop instance, this method requires
    a DirectoryEntryQueryset of SecureDrop instances that are in the database
    and always commits the results back to the database.
    """

    # Ensure that we have the domain annotation present
    securedrops = securedrops.with_domain_annotation()
    domains = securedrops.values_list('domain', flat=True)

    # Send the domains to pshtt. This will trigger HTTP requests for each domain
    # and can take some time!
    results = inspect_domains(domains, {'timeout': 10})

    results_to_be_written = []
    for result_data in results:
        securedrop = securedrops.get(domain=result_data['Domain'])
        current_result = pshtt_data_to_result(securedrop, result_data)

        # These are usually handled by Result.save, but since we're doing a
        # bulk save, we need to do them here first
        current_result.compute_grade()
        current_result.securedrop = securedrop

        # Before we save, let's get the most recent scan before saving
        try:
            prior_result = securedrop.results.latest()
        except ScanResult.DoesNotExist:
            results_to_be_written.append(current_result)
            continue

        if prior_result.is_equal_to(current_result):
            # Then let's not waste a row in the database
            prior_result.result_last_seen = timezone.now()
            prior_result.save()
        else:
            # Then let's add this new scan result to the database
            results_to_be_written.append(current_result)

    # Write new results to the db in a batch
    return ScanResult.objects.bulk_create(results_to_be_written)


def request_and_scrape_page(url, allow_redirects=True):
    """Scrape and parse the HTML of a page into a BeautifulSoup"""
    try:
        page = requests.get(url, allow_redirects=allow_redirects)
        soup = BeautifulSoup(page.content, "lxml")
    except requests.exceptions.MissingSchema:
        page = requests.get('https://{}'.format(url), allow_redirects=allow_redirects)
        soup = BeautifulSoup(page.content, "lxml")

    return page, soup


def validate_subdomain(url):
    """Is the landing page on a subdomain"""
    parsed_domain = tldextract.extract(url)
    return parsed_domain.subdomain not in ('', 'www')


def validate_not_using_cdn(page):
    """Right now this is just checking for Cloudflare"""
    if 'CF-Cache-Status' in page.headers or 'CF-RAY' in page.headers:
        return False
    else:
        return True


def validate_not_using_analytics(page):
    """Scan for common analytics scripts anywhere in the page

    Google Analytics: https://support.google.com/analytics/answer/1032399?hl=en

    Chartbeat: http://support.chartbeat.com/docs/

    Quantcast: https://quantcast.zendesk.com/hc/en-us/articles/115014888548--Implement-Quantcast-Tag-Directly-on-Your-Site

    comScore: http://www.scorecardresearch.com/ (no public docs)

    Krux Digital: https://whotracks.me/trackers/krux_digital.html#News%20and%20Portals
    """
    # Common scripts: Google Analytics, Quantcast, Chartbeat (two variants),
    # comScore
    analytics_scripts = ('ga.js', 'analytics.js', 'quant.js',
                         'chartbeat.js', 'chartbeat_mab.js', 'beacon.js',
                         'krxd.net')
    page_str = str(page.content)
    for script in analytics_scripts:
        if script in page_str:
            return False

    # No recognized script in page body
    return True


def validate_security_header(page, header, expected_value):
    if header not in page.headers:
        return False
    elif page.headers[header] == expected_value:
        return True
    else:
        return False


def validate_cache_control_header(page, expected_directive):
    header = page.headers.get('Cache-Control', '')
    directives = [directive.lower().strip() for directive in header.split(',')]

    return expected_directive in directives


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
    if page.encoding is None:
        return False
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
    return validate_cache_control_header(page, 'must-revalidate')


def validate_nocache(page):
    return validate_cache_control_header(page, 'no-cache')


def validate_nostore(page):
    return validate_cache_control_header(page, 'no-store')


def validate_notransform(page):
    return validate_cache_control_header(page, 'no-transform')


def validate_private(page):
    return validate_cache_control_header(page, 'private')


def validate_no_referrer_policy(page):
    return validate_security_header(page, "Referrer-Policy", "no-referrer")


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
