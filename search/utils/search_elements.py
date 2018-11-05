from django.db.models import Value
from django.contrib.postgres.search import SearchVector


class SearchElements(object):
    def __init__(self):
        self.text = []
        self.vector = SearchVector(Value(''))

    def append(self, text, weight=None):
        self.text.append(text)

        new_vector = SearchVector(Value(text), weight=weight)
        self.vector = self.vector + new_vector

    def as_string(self):
        return '\n'.join(self.text)

    def as_search_vector(self):
        return self.vector
