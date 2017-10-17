import random
import string

import factory

import wagtail_factories
from landing_page_checker.models import SecuredropPage
from directory.tests.factories import LanguageFactory, CountryFactory, TopicFactory


def random_onion_address():
    return 'https://' + ''.join(
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

    @factory.post_generation
    def countries(self, create, count):
        if count is None:
            count = 2
        make_country = getattr(CountryFactory, 'create' if create else 'build')
        countries = []
        for i in range(count):
            country = make_country()
            country.save()
            country.countries.add(self)
            countries.append(country)
        if not create:
            self._prefetched_objects_cache = {'countries': countries}

    @factory.post_generation
    def topics(self, create, count):
        if count is None:
            count = 2
        make_topic = getattr(TopicFactory, 'create' if create else 'build')
        topics = []
        for i in range(count):
            topic = make_topic()
            topic.save()
            topic.topics.add(self)
            topics.append(topic)
        if not create:
            self._prefetched_objects_cache = {'topics': topics}
