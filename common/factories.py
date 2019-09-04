from factory import (
    DjangoModelFactory,
    Faker,
    SubFactory,
)
from wagtail_factories import PageFactory, ImageFactory

from common.models import Button, CustomImage


class ButtonFactory(DjangoModelFactory):
    class Meta:
        model = Button

    text = Faker('sentence', nb_words=3)
    link = SubFactory(PageFactory)


class CustomImageFactory(ImageFactory):
    attribution = Faker('name')

    class Meta:
        model = CustomImage
