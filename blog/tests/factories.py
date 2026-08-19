from datetime import UTC

import factory
import wagtail_factories

from blog.models import BlogIndexPage, BlogPage, CategoryPage


class BlogIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = BlogIndexPage

    title = factory.Faker("sentence")


class CategoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = CategoryPage

    description = factory.Faker("paragraph")
    title = factory.Faker("sentence", nb_words=3)


class BlogPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = BlogPage

    publication_datetime = factory.Faker(
        "date_time_this_month", after_now=False, before_now=True, tzinfo=UTC
    )
    title = factory.Faker("sentence")
    category = factory.SubFactory(CategoryPageFactory)
