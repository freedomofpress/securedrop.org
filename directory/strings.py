SEVERE_WARNINGS = [
    ('no_cdn', '{} uses a CDN.'),
    ('no_analytics', '{} uses analytics. Visiting this SecureDrop landing page may directly reveal information about your browsing behavior to third parties beyond the organization that operates the SecureDrop instance.'),
]

MODERATE_WARNINGS = [
    ('subdomain', '{0} is hosted on a subdomain, "{domain}", which is unencrypted metadata that could be monitored by a third party.'),
    ('referrer_policy_set_to_no_referrer', '{} does not <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy">suppress referrers</a>. Following any links on the page may reveal your visit of the page to third parties.'),
    ('safe_onion_address', '{} includes a clickable link to a Tor Onion Service (.onion address). Any attempt to visit such a link in a regular browser will fail, but it may be detected by third parties.'),
]
