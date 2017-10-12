import factory
import wagtail_factories

from directory.models import DirectoryPage, Language, Country, Topic


class DirectoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = DirectoryPage
    parent = factory.SubFactory(wagtail_factories.PageFactory, parent=None)
    title = factory.Faker('sentence')


class LanguageFactory(factory.Factory):
    class Meta:
        model = Language
    title = factory.Faker('word')


class CountryFactory(factory.Factory):
    class Meta:
        model = Country
    title = factory.Faker('word')


class TopicFactory(factory.Factory):
    class Meta:
        model = Topic
    title = factory.Faker('word')
