from datetime import UTC, datetime, timedelta

from factory import (
    Faker,
    LazyAttributeSequence,
    Sequence,
    SubFactory,
)
from factory.django import DjangoModelFactory

from github.models import Product, Release


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
        django_get_or_create = ("repo_full_name",)

    name = Sequence(lambda n: f"Product {n}")
    repo_full_name = Sequence(lambda n: f"freedomofpress/product-{n}")


class ReleaseFactory(DjangoModelFactory):
    class Meta:
        model = Release

    product = SubFactory(ProductFactory)
    url = Faker("url")
    tag_name = LazyAttributeSequence(lambda o, n: f"{o.date.year}.{n}")
    date = Sequence(lambda n: datetime(2018, 1, 1, tzinfo=UTC) + timedelta(days=n * n))
