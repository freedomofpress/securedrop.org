from django.contrib.postgres.search import SearchVector
from django.db.models import TextField, Value


class SearchElements:
    def __init__(self):
        self.text = []
        self.vector = SearchVector(Value("", output_field=TextField()))

    def append(self, text, weight=None):
        self.text.append(text)

        new_vector = SearchVector(
            Value(text, output_field=TextField()),
            weight=weight,
        )
        self.vector = self.vector + new_vector

    def as_string(self):
        return "\n".join(self.text)

    def as_search_vector(self):
        return self.vector
