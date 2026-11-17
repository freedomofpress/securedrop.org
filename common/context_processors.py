from django.conf import settings


def analytics(request):
    return {"analytics_enabled": settings.ANALYTICS_ENABLED}
