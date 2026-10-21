# Lightweight settings overrides for the QA stack

from .production import *


# Production hard-codes analytics on; keep test runs out of the real analytics.
ANALYTICS_ENABLED = False

# Still enforce the CSP, so tests can catch violations, but don't report them
# to the production report-uri endpoint.
CONTENT_SECURITY_POLICY["DIRECTIVES"].pop("report-uri", None)

# Print email contents to the console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
