"""Sanitize production database for securedrop.org environments.

Usage:
    python manage.py sanitize -r hostname=staging.securedrop.org

    # Skip interactive confirmation prompt
    python manage.py sanitize -r hostname=staging.securedrop.org --confirm

    # Preserve CMS users:
    python manage.py sanitize -r hostname=staging.securedrop.org --confirm --no-mangle auth.User

    # Preserve Django session data:
    python manage.py sanitize -r hostname=dev.securedrop.org --confirm --no-truncate sessions.Session
"""

from fpfwagtailcommon.utils.management.commands.sanitize_base import (
    SanitizationProfile,
    SanitizeBaseCommand,
)


class Command(SanitizeBaseCommand):
    help = "Sanitize a securedrop.org database"

    profile = SanitizationProfile(
        mangle_tables={
            "auth.User": {
                "password": "[REDACTED]",
                "email": "no-reply@invalid.freedom.press",
            },
            "wagtailcore.Site": {
                "hostname": "{hostname}",
            },
        },
        truncate_tables=[
            "sessions.Session",
            "wagtailforms.FormSubmission",
        ],
    )
