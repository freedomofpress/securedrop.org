from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from wagtail.models import Page
from wagtail.signals import page_published
from wagtail.contrib.settings.models import BaseSiteSetting

from cloudflare.utils import purge_all_from_cache


@receiver([pre_delete, page_published], sender=Page)
def purge_cache_for_pages(sender, **kwargs):
    """
    We're using the nuclear option for caching. Every time any Page changes
    we flush the entire cache
    """
    purge_all_from_cache()


@receiver([pre_delete, post_save])
def purge_cache_for_settings(sender, **kwargs):
    """
    We're using the nuclear option for caching. Every time any Setting changes
    we flush the entire cache
    """
    if issubclass(sender, BaseSiteSetting):
        purge_all_from_cache()
