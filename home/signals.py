from django.db.models.signals import post_save, post_delete

from wagtail.contrib.frontend_cache.utils import purge_page_from_cache

from home.models import HomePage
from github.models import Release
from blog.models import BlogPage
from directory.models import DirectoryEntry


def purge_homepage_from_frontend_cache(sender, **kwargs):
    for home_page in HomePage.objects.live():
        purge_page_from_cache(home_page)


post_save.connect(purge_homepage_from_frontend_cache, sender=Release)
post_save.connect(purge_homepage_from_frontend_cache, sender=BlogPage)
post_save.connect(purge_homepage_from_frontend_cache, sender=DirectoryEntry)
post_delete.connect(purge_homepage_from_frontend_cache, sender=Release)
post_delete.connect(purge_homepage_from_frontend_cache, sender=BlogPage)
post_delete.connect(purge_homepage_from_frontend_cache, sender=DirectoryEntry)
