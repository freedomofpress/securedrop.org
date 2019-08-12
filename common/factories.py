from factory import (
    DjangoModelFactory,
    Faker,
    SubFactory,
)
from wagtail_factories import PageFactory

from common.models import Button

class ButtonFactory(DjangoModelFactory):
    class Meta:
        model = Button

    text = Faker('sentence', nb_words=3)
    link = SubFactory(PageFactory)
