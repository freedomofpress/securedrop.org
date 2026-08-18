import factory

from search.models import SearchDocument


class SearchDocumentFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: f"Document {n}")
    data = {}
    key = factory.Sequence(lambda n: f"Key {n}")

    class Meta:
        model = SearchDocument
