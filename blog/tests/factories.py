from datetime import timezone

import factory
import wagtail_factories

from blog.models import BlogPage, BlogIndexPage
from common.tests.factories import PersonPageFactory, OrganizationPageFactory


class BlogIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = BlogIndexPage

    parent = factory.SubFactory(wagtail_factories.PageFactory, parent=None)


class BlogPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = BlogPage
    publication_datetime = factory.Faker(
        'date_time_this_month', after_now=False, before_now=True,
        tzinfo=timezone.utc)
    parent = factory.SubFactory(BlogIndexPageFactory)
    author = factory.SubFactory(PersonPageFactory)
    organization = factory.SubFactory(OrganizationPageFactory)
