import factory
import wagtail_factories

from marketing.models import MarketingIndexPage


class MarketingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = MarketingIndexPage
    parent = factory.SubFactory(wagtail_factories.PageFactory, parent=None)
    title = factory.Faker('sentence')
