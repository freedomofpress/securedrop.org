from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from github.models import Release

from cloudflare.utils import purge_all_from_cache


@receiver([post_save, pre_delete], sender=Release)
def purge_cache(sender, **kwargs):
    """
    We're using the nuclear option for caching. Every time a Release changes
    we flush the entire cache
    """
    purge_all_from_cache()
