import factory

from directory.models import Language, Country, Topic


class LanguageFactory(factory.Factory):
    class Meta:
        model = Language
    # there were not suffient random words in faker, so we're using sentences
    title = factory.Faker('sentence', nb_words=3)


class CountryFactory(factory.Factory):
    class Meta:
        model = Country
    title = factory.Faker('sentence', nb_words=3)


class TopicFactory(factory.Factory):
    class Meta:
        model = Topic
    title = factory.Faker('sentence', nb_words=3)
