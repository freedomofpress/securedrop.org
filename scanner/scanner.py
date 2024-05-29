from bs4 import BeautifulSoup
import requests
import re
import itertools
import operator

from typing import TYPE_CHECKING, Tuple, Dict, List

import tldextract

from django.utils import timezone

from directory.models import ScanResult, DirectoryEntry
from scanner.utils import HEADERS
from scanner.assets import extract_assets, Asset
from scanner.http2 import check_http2


if TYPE_CHECKING:
    from directory.models import DirectoryEntryQuerySet  # noqa: F401


def perform_scan(url: str, permitted_domains: List[str]) -> ScanResult:
    scan_data = {
        'live': False,
        'landing_page_url': url,
    }

    try:
        page, soup = request_and_scrape_page(url)

    except requests.exceptions.RequestException:
        # Connection timed out, an invalid HTTP response was returned, or
        # a network problem occurred.
        # Catch the base class exception for these cases.
        scan_data['http_status_200_ok'] = False
        return ScanResult(**scan_data)
    scan_data['live'] = True

    http_response_data = parse_page_data(page)
    scan_data.update(http_response_data)

    content_data = parse_soup_data(soup)
    scan_data.update(content_data)

    assets = extract_assets(soup, page.url)
    asset_results = parse_assets(assets, [tldextract.extract(page.url).registered_domain] + permitted_domains)
    scan_data.update(asset_results)

    if page.url:
        http2_data = check_http2(page.url)
    else:
        http2_data = {'http2': False}
    scan_data.update(http2_data)

    return ScanResult(**scan_data)


def scan(entry: DirectoryEntry, commit=False) -> ScanResult:
    """
    Scan a single site. This method accepts a DirectoryEntry instance which
    may or may not be saved to the database. You can optionally pass True for
    the commit argument, which will save the result to the database. In that
    case, the passed DirectoryEntry *must* already be in the database.
    """
    permitted_domains = [
        tldextract.extract(d).registered_domain
        for d in entry.permitted_domains_for_assets
    ]
    result = perform_scan(entry.landing_page_url, permitted_domains)

    if commit:
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

    results_to_be_written = []
    for entry in securedrops:
        permitted_domains = [
            tldextract.extract(d).registered_domain
            for d in entry.permitted_domains_for_assets
        ]
        try:
            current_result = perform_scan(entry.landing_page_url, permitted_domains)
        except Exception:
            continue

        # This is usually handled by Result.save, but since we're doing a
        # bulk save, we need to do it here
        current_result.securedrop = entry

        # Before we save, let's get the most recent scan before saving
        try:
            prior_result = entry.results.latest()
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


def request_and_scrape_page(url: str, allow_redirects: bool = True) -> Tuple[requests.models.Response, BeautifulSoup]:
    """Scrape and parse the HTML of a page into a BeautifulSoup"""

    # Note: headers include User-Agent which is required for correct
    # scanning.
    try:
        page = requests.get(
            url,
            allow_redirects=allow_redirects,
            headers=HEADERS,
            timeout=10,
        )
        soup = BeautifulSoup(page.content, "lxml")
    except requests.exceptions.MissingSchema:
        page = requests.get(
            'https://{}'.format(url),
            allow_redirects=allow_redirects,
            headers=HEADERS,
            timeout=10,
        )
        soup = BeautifulSoup(page.content, "lxml")

    return page, soup


def parse_page_data(page: requests.models.Response) -> Dict[str, bool]:
    http_response_data = {
        'no_cross_domain_redirects': True,
        'subdomain': validate_subdomain(page.url),
        'http_status_200_ok': validate_200_ok(page),
        'no_cookies': validate_no_cookies(page),
        'no_cdn': validate_not_using_cdn(page),
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
        'referrer_policy_set_to_no_referrer': validate_no_referrer_policy(page),
    }
    if page.history:
        http_response_data['redirect_target'] = page.url

        for response in page.history:
            if validate_subdomain(response.url):
                http_response_data['subdomain'] = True
            if not same_domain(response.url, page.url):
                http_response_data['no_cross_domain_redirects'] = False

    return http_response_data


def parse_assets(assets, permitted_domains: List[str]) -> Dict[str, bool]:
    summary = ''
    ignored_summary = ''
    no_cross_domain_assets = True

    third_party_assets = []
    ignored_assets = []

    for asset in assets:
        # ignore subdomain attribute
        extracted = tldextract.extract(asset.resource)
        (_, asset_domain, asset_suffix) = extracted
        if not (asset_domain and asset_suffix):
            # we've extracted something that probably is not a real domain
            continue

        if extracted.registered_domain in permitted_domains:
            continue

        # Ignore 'script-resource' and 'script-embed' assets, these
        # are causing a lot of false positives
        if asset.kind in ('script-resource', 'script-embed'):
            ignored_assets.append(asset)
            continue

        third_party_assets.append(asset)

    if ignored_assets:
        ignored_summary = summarize_assets(ignored_assets)

    if third_party_assets:
        no_cross_domain_assets = False
        summary = summarize_assets(third_party_assets)

    return {
        'ignored_cross_domain_assets': ignored_summary,
        'no_cross_domain_assets': no_cross_domain_assets,
        'cross_domain_asset_summary': summary,
    }


def summarize_assets(assets: List[Asset]) -> str:
    summary = ''

    by_initiator = operator.attrgetter('initiator')
    by_kind = operator.attrgetter('kind')

    sorted_assets = sorted(assets, key=by_initiator)

    for initiator, assets in itertools.groupby(sorted_assets, by_initiator):
        summary += initiator + '\n'
        for asset in sorted(assets, key=by_kind):
            summary += '  * ({0.kind}) {0.resource}\n'.format(asset)
    return summary


def parse_soup_data(soup: BeautifulSoup) -> Dict[str, bool]:
    return {
        'safe_onion_address': validate_onion_address_not_in_href(soup),
    }


def same_domain(url1: str, url2: str) -> bool:
    parsed_url1 = tldextract.extract(url1)
    parsed_url2 = tldextract.extract(url2)

    return (parsed_url1.domain == parsed_url2.domain and
            parsed_url1.suffix == parsed_url2.suffix)


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
