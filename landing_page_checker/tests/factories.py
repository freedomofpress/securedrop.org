import random
import string

import factory
from django.utils.text import slugify

import wagtail_factories
from directory.tests.factories import DirectoryPageFactory
from landing_page_checker.models import SecuredropPage


def random_onion_address():
    return ''.join(
        random.choice(string.ascii_lowercase + string.digits)
        for _ in range(16)
    ) + '.onion'


class SecuredropPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = SecuredropPage

    title = factory.Faker('sentence', nb_words=3)
    landing_page_domain = factory.Faker('uri')
    onion_address = factory.LazyFunction(random_onion_address)
    parent = None
