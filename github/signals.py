from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from cloudflare.utils import purge_all_from_cache
from github.models import Product, Release


@receiver([post_save, pre_delete], sender=Release)
@receiver([post_save, pre_delete], sender=Product)
def purge_cache(sender, **kwargs):
    """
    We're using the nuclear option for caching. Every time a Release or
    Product changes we flush the entire cache.
    """
    purge_all_from_cache()
