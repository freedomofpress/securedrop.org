from django.db.models.signals import post_delete, post_save

from wagtail.wagtailcore.signals import page_published, page_unpublished
from wagtail.wagtailcore.models import Page

from search.utils.wagtail import delete_wagtail_page, index_wagtail_page


def index_wagtail_page_(sender, instance, **kwargs):
    return index_wagtail_page(instance)


def delete_wagtail_page_(sender, instance, **kwargs):
    return delete_wagtail_page(instance)


page_published.connect(index_wagtail_page_)
page_unpublished.connect(delete_wagtail_page_)
