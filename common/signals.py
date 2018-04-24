from django.db.models.signals import pre_delete
from django.dispatch import receiver
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.signals import page_published

from cloudflare.utils import purge_all_from_cache


@receiver([pre_delete, page_published], sender=Page)
def purge_cache(sender, **kwargs):
    """
    We're using the nuclear option for caching. Every time any page changes
    we flush the entire cache
    """
    purge_all_from_cache()
