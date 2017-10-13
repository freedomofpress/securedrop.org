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
