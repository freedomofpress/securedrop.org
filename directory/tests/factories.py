import random
import string

import factory
import wagtail_factories

from directory.models import SecureDropInstance, DirectoryPage


class DirectoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = DirectoryPage
    parent = factory.SubFactory(wagtail_factories.PageFactory, parent=None)
    title = factory.Faker('sentence')


class SecureDropInstanceFactory(factory.Factory):
    class Meta:
        model = SecureDropInstance

    sort_order = factory.Sequence(lambda n: n)
    page = factory.SubFactory(DirectoryPageFactory)
    onion_address = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
    landing_page = factory.Faker('uri')
    organization = factory.Faker('sentence', nb_words=3)
