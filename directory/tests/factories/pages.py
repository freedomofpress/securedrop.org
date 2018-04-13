import factory
import wagtail_factories

from directory.models import DirectoryPage


class DirectoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = DirectoryPage
    parent = factory.SubFactory(wagtail_factories.PageFactory, parent=None)
    title = factory.Faker('sentence')
