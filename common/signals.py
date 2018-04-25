from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.signals import page_published
from wagtail.contrib.settings.models import BaseSetting

from cloudflare.utils import purge_all_from_cache


@receiver([pre_delete, page_published], sender=Page)
def purge_cache_for_pages(sender, **kwargs):
    """
    We're using the nuclear option for caching. Every time any Page changes
    we flush the entire cache
    """
    purge_all_from_cache()


@receiver([pre_delete, post_save], sender=BaseSetting)
def purge_cache_for_settings(sender, **kwargs):
    """
    We're using the nuclear option for caching. Every time any Setting changes
    we flush the entire cache
    """
    purge_all_from_cache()
