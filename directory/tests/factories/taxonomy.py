import factory

from directory.models import Language, Country, Topic


class LanguageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Language
        django_get_or_create = ('title',)
    # there were not suffient random words in faker, so we're using sentences
    title = factory.Faker('sentence', nb_words=3)


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ('title',)
    title = factory.Faker('sentence', nb_words=3)


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Topic
        django_get_or_create = ('title',)
    title = factory.Faker('sentence', nb_words=3)
