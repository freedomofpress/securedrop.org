from factory import (
    Faker,
    DjangoModelFactory,
    Iterator,
    Sequence,
    SubFactory,
    Trait,
)
from wagtail_factories import PageFactory

from common.models import CustomImage
from marketing.models import (
    MarketingIndexPage,
    FeaturePage,
    OrderedFeatures,
)


class MarketingPageFactory(PageFactory):
    class Meta:
        model = MarketingIndexPage
    title = Faker('sentence')


class FeaturePageFactory(PageFactory):
    class Meta:
        model = FeaturePage

    class Params:
        with_image = Trait(
            icon=Iterator(CustomImage.objects.filter(collection__name='Icons'))
        )

    title = Faker('sentence')
    teaser_title = Faker('sentence', nb_words=3)
    teaser_description = Faker('sentence')
    description = Faker('paragraph', nb_sentences=5, variable_nb_sentences=True)


class OrderedFeaturesFactory(DjangoModelFactory):
    class Meta:
        model = OrderedFeatures

    sort_order = Sequence(int)
    page = SubFactory(MarketingPageFactory)
    feature = SubFactory(FeaturePageFactory)
