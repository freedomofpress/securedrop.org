from datetime import timezone, timedelta, datetime

from factory import (
    DjangoModelFactory,
    Faker,
    Sequence,
    LazyAttributeSequence,
)

from github.models import Release


class ReleaseFactory(DjangoModelFactory):
    class Meta:
        model = Release

    url = Faker('url')
    tag_name = LazyAttributeSequence(
        lambda o, n: "{year}.{n}".format(year=o.date.year, n=n)
    )
    date = Sequence(
        lambda n: datetime(2018, 1, 1, tzinfo=timezone.utc) + timedelta(days=n * n)
    )
