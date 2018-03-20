import re

from requests.api import get
from requests.exceptions import ConnectionError


NON_EXISTENT_URL = 'https://notarealsite.party'
NON_EXISTENT_URL_RE = url_re = re.compile(r'https?://(www\.)?notarealsite\.party(/.*)?')


def requests_get_mock(url, params={}, **kwargs):
    """
    A replacement for requests.api.get that raises a ConnectionError if it is
    passed any variation on the domain 'notarealsite.party' and passes through
    to the original requests.api.get otherwise. Useful to test requesting
    non-existent domains without actually firing http requests.
    """
    if NON_EXISTENT_URL_RE.fullmatch(url):
        raise ConnectionError
    else:
        return get(url, params, **kwargs)
