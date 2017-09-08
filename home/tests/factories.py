import factory
import wagtail_factories

from home.models import HomePage


class HomePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = HomePage

    title = 'SecureDrop'
    slug = 'home'
    description_header = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text')
    features_header = 'What SecureDrop Does'
    parent = None
