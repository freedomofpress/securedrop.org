import re


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
    return validate_security_header(
        page,
        "Content-Security-Policy",
        "default-src 'self'",
    )


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
