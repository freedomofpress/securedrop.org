from factory import (
    Faker,
    Sequence,
    SubFactory,
)
from factory.django import DjangoModelFactory
from wagtail_factories import PageFactory

from common.factories import ButtonFactory
from home.models import (
    FeaturesButton,
    HomePage,
    HomePageInstances,
    HomepageFeature,
    InstancesButton,
)


class HomePageFactory(PageFactory):
    class Meta:
        model = HomePage

    title = 'SecureDrop'
    slug = 'home'
    description_header = Faker('sentence', nb_words=4)
    description = Faker('text')
    features_header = 'What SecureDrop Does'


class HomePageInstancesFactory(DjangoModelFactory):
    class Meta:
        model = HomePageInstances

    sort_order = Sequence(int)
    page = SubFactory(HomePageFactory)
    instance = None


class HomepageFeatureFactory(DjangoModelFactory):
    class Meta:
        model = HomepageFeature
    sort_order = Sequence(int)
    page = SubFactory(HomePageFactory)
    feature = None


class InstancesButtonFactory(ButtonFactory):
    class Meta:
        model = InstancesButton

    page = SubFactory(HomePageFactory)


class FeaturesButtonFactory(ButtonFactory):
    class Meta:
        model = FeaturesButton

    page = SubFactory(HomePageFactory)
