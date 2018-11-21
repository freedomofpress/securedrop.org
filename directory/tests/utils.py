import re


NON_EXISTENT_URL = 'https://notarealsite.party'
NON_EXISTENT_URL_RE = url_re = re.compile(r'https?://(www\.)?notarealsite\.party(/.*)?')


def perform_scan_mock(url):
    """A replacement for scanner.perform_scan that returns fake scan data

    If this function is passed any variation of the domain
    'notarealsite.party', then it returns data for a non-live landing
    page, otherwise returns data for a live site.  In either case, the
    data is very stripped-down.

    """
    if NON_EXISTENT_URL_RE.fullmatch(url):
        return {
            'live': False,
            'landing_page_url': url,
            'http_status_200_ok': False,
        }
    else:
        return {
            'live': True,
            'landing_page_url': url,
            'http_status_200_ok': True,
        }
