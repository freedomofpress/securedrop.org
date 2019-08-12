from factory import (
    Faker,
    DjangoModelFactory,
    Sequence,
    SubFactory,
)
from wagtail_factories import PageFactory

from common.factories import ButtonFactory
from home.models import HomePage, HomePageInstances, InstancesButton


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


class InstancesButtonFactory(ButtonFactory):
    class Meta:
        model = InstancesButton

    page = SubFactory(HomePageFactory)
