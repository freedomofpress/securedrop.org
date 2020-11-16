import factory

from directory.models import Language, Country, Topic


class LanguageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Language
        django_get_or_create = ('title',)
    title = factory.Faker('language_name')


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ('title',)
    title = factory.Faker('country')


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Topic
        django_get_or_create = ('title',)
    title = factory.Iterator([
        'Algebra',
        'Applied Mathematics',
        'Calculus and Analysis',
        'Discrete Mathematics',
        'Foundations of Mathematics',
        'Geometry',
        'History and Terminology',
        'Number Theory',
        'Probability and Statistics',
        'Recreational Mathematics',
        'Topology',
    ])
