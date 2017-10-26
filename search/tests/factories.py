import factory

from search.models import SearchDocument


class SearchDocumentFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Document {}'.format(n))
    data = {}
    key = factory.Sequence(lambda n: 'Key {}'.format(n))

    class Meta:
        model = SearchDocument
