from datetime import timezone, timedelta, datetime

from factory import (
    Faker,
    Sequence,
    LazyAttributeSequence,
    SubFactory,
)
from factory.django import DjangoModelFactory

from github.models import Product, Release


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
        django_get_or_create = ("repo_full_name",)

    name = Sequence(lambda n: "Product {}".format(n))
    repo_full_name = Sequence(lambda n: "freedomofpress/product-{}".format(n))


class ReleaseFactory(DjangoModelFactory):
    class Meta:
        model = Release

    product = SubFactory(ProductFactory)
    url = Faker("url")
    tag_name = LazyAttributeSequence(
        lambda o, n: "{year}.{n}".format(year=o.date.year, n=n)
    )
    date = Sequence(
        lambda n: datetime(2018, 1, 1, tzinfo=timezone.utc) + timedelta(days=n * n)
    )
