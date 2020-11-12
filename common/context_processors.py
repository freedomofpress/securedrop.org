from django.conf import settings


def analytics_variables(request):
    return {
        'PIWIK_DOMAIN_PATH': settings.PIWIK_DOMAIN_PATH,
        'PIWIK_SITE_ID': settings.PIWIK_SITE_ID,
    }
