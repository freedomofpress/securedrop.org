SEVERE_WARNINGS = [
    ('no_cookies', '{} uses cookies.'),
    ('no_cdn', '{} uses a CDN.'),
    ('no_analytics', '{} uses analytics.'),
]

MODERATE_WARNINGS = [
    ('subdomain', '{0} is hosted on a subdomain, "{domain}", which is unencrypted metadata that may be monitored.'),
    ('referrer_policy_set_to_no_referrer', '{} uses the wrong referrer policy.'),
    ('safe_onion_address', '{} contains clickable onion addresses. '),
]
