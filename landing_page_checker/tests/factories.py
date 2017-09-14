import random
import string

import factory
from django.utils.text import slugify

from directory.tests.factories import DirectoryPageFactory
from landing_page_checker.models import Securedrop


class SecuredropFactory(factory.Factory):
    class Meta:
        model = Securedrop

    page = factory.SubFactory(DirectoryPageFactory)
    organization = factory.Faker('sentence', nb_words=3)
    slug = factory.LazyAttribute(lambda o: slugify(o.organization))
    landing_page_domain = factory.Faker('uri')
    onion_address = (
        ''.join(
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(16)
        )
    )
