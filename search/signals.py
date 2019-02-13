from wagtail.core.signals import page_published, page_unpublished

from search.utils.wagtail import delete_wagtail_page, index_wagtail_page


def index_wagtail_page_(sender, instance, **kwargs):
    return index_wagtail_page(instance)


def delete_wagtail_page_(sender, instance, **kwargs):
    return delete_wagtail_page(instance)


page_published.connect(index_wagtail_page_)
page_unpublished.connect(delete_wagtail_page_)
