import random
import string

import factory

import wagtail_factories
from landing_page_checker.models import SecuredropPage
from directory.tests.factories import LanguageFactory


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

    @factory.post_generation
    def languages(self, create, count):
        if count is None:
            count = 2
        make_language = getattr(LanguageFactory, 'create' if create else 'build')
        languages = []
        for i in range(count):
            lang = make_language()
            lang.save()
            lang.languages.add(self)
            languages.append(lang)
        if not create:
            self._prefetched_objects_cache = {'languages': languages}
