import factory
import wagtail_factories

from directory.models import DirectoryPage


class DirectoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = DirectoryPage
    title = factory.Faker('sentence')
