import factory
import wagtail_factories

from marketing.models import MarketingIndexPage


class MarketingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = MarketingIndexPage
    title = factory.Faker('sentence')
