import factory

from search.models import SearchDocument


class SearchDocumentFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Document {}'.format(n))
    data = {}

    class Meta:
        model = SearchDocument
