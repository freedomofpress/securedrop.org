from django.core.management.base import BaseCommand
from django.db import transaction

from home.models import HomePage
from home.tests.factories import HomepageFeatureFactory, FeaturesButtonFactory
from marketing.models import MarketingIndexPage
from marketing.tests.factories import FeaturePageFactory, OrderedFeaturesFactory


class Command(BaseCommand):
    help = 'Creates marketing data appropriate for development'

    @transaction.atomic
    def handle(self, *args, **options):
        home_page = HomePage.objects.get(slug='home')

        marketing_index = MarketingIndexPage.objects.first()

        features = FeaturePageFactory.create_batch(
            5,
            parent=marketing_index,
            with_image=True,
        )
        for feature in features:
            OrderedFeaturesFactory(page=marketing_index, feature=feature)
            HomepageFeatureFactory(page=home_page, feature=feature)
        FeaturesButtonFactory(
            page=home_page,
            link=marketing_index,
            text='Learn more about SecureDrop',
        )
