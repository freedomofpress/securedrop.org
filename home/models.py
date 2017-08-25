from wagtail.wagtailcore.models import Page
from common.models import MetadataPageMixin


class HomePage(MetadataPageMixin, Page):
    pass
