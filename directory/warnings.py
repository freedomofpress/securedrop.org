from dataclasses import dataclass
from enum import Enum
from collections.abc import Callable

import directory.models.entry


class TestResult(Enum):
    PASS = 1
    FAIL = 2


class WarningLevel(Enum):
    NONE = 0
    MODERATE = 1
    SEVERE = 2

    @property
    def is_moderate(self):
        return self == WarningLevel.MODERATE

    @property
    def is_severe(self):
        return self == WarningLevel.SEVERE


@dataclass
class Warning:
    name: str
    test: Callable[['directory.models.entry.ScanResult'], TestResult]
    level: WarningLevel
    message: str


def unreachable_test(scan_result):
    if not scan_result.http_status_200_ok:
        return TestResult.FAIL
    else:
        return TestResult.PASS


def onion_address_test(scan_result):
    if scan_result.safe_onion_address:
        return TestResult.PASS
    else:
        return TestResult.FAIL


def referrer_policy_test(scan_result):
    if scan_result.referrer_policy_set_to_no_referrer:
        return TestResult.PASS
    else:
        return TestResult.FAIL


def subdomain_test(scan_result):
    if scan_result.subdomain:
        return TestResult.FAIL
    else:
        return TestResult.PASS


def third_party_asset_test(scan_result):
    if scan_result.no_analytics and scan_result.no_cross_domain_assets:
        return TestResult.PASS
    else:
        return TestResult.FAIL


WARNINGS = [
    Warning(
        'no_third_party_assets',
        third_party_asset_test,
        WarningLevel.SEVERE,
        '{} uses assets hosted on a separate domain. Visiting this SecureDrop landing page may directly reveal information about your browsing behavior to third parties beyond the organization that operates the SecureDrop instance.',
    ),
    Warning(
        'subdomain',
        subdomain_test,
        WarningLevel.MODERATE,
        '{0} is hosted on a subdomain, "{domain}", which is unencrypted metadata that could be monitored by a third party.',
    ),
    Warning(
        'referrer_policy_set_to_no_referrer',
        referrer_policy_test,
        WarningLevel.MODERATE,
        '{} does not <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy">suppress referrers</a>. Following any links on the page may reveal your visit of the page to third parties.'
    ),
    Warning(
        'safe_onion_address',
        onion_address_test,
        WarningLevel.MODERATE,
        '{} includes a clickable link to a Tor Onion Service (.onion address). Any attempt to visit such a link in a regular browser will fail, but it may be detected by third parties.',
    ),
    Warning(
        'unreachable_landing_page',
        unreachable_test,
        WarningLevel.SEVERE,
        "This SecureDrop's landing page appears to be unreachable. You may wish to wait until the landing page is back online before contacting this SecureDrop, so you can verify the .onion address.",
    )
]


SEVERE_WARNINGS = [
    ('no_cdn', '{} uses a CDN.'),
    ('no_cross_domain_assets', 'Visiting this SecureDrop landing page may directly reveal information about your browsing behavior to third parties beyond the organization that operates the SecureDrop instance.'),
    ('no_analytics', '{} uses assets hosted on a separate domain. Visiting this SecureDrop landing page may directly reveal information about your browsing behavior to third parties beyond the organization that operates the SecureDrop instance.'),
]

MODERATE_WARNINGS = [
    ('subdomain', '{0} is hosted on a subdomain, "{domain}", which is unencrypted metadata that could be monitored by a third party.'),
    ('referrer_policy_set_to_no_referrer', '{} does not <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy">suppress referrers</a>. Following any links on the page may reveal your visit of the page to third parties.'),
    ('safe_onion_address', '{} includes a clickable link to a Tor Onion Service (.onion address). Any attempt to visit such a link in a regular browser will fail, but it may be detected by third parties.'),
]
