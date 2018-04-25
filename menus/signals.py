from django.db.models.signals import post_save, post_delete

from cloudflare.utils import purge_all_from_cache
from menus.models import Menu, MenuItem


def purge_all(sender, **kwargs):
    purge_all_from_cache()


post_save.connect(purge_all, sender=Menu)
post_save.connect(purge_all, sender=MenuItem)
post_delete.connect(purge_all, sender=Menu)
post_delete.connect(purge_all, sender=MenuItem)
