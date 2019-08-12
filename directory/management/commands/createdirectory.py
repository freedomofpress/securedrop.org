from django.db import transaction
from django.core.management.base import BaseCommand

from directory.models import DirectoryPage
from directory.tests.factories import (
    DirectoryPageFactory,
    DirectoryEntryFactory,
    ScanResultFactory,
)
from home.models import HomePage
from home.tests.factories import HomePageInstancesFactory, InstancesButtonFactory


class Command(BaseCommand):
    help = 'Creates directory of securedrop instances for development'

    def add_arguments(self, parser):
        parser.add_argument('number_of_instances', type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        number_of_instances = options['number_of_instances']

        home_page = HomePage.objects.get(slug='home')
        directory = DirectoryPage.objects.first()
        if not directory:
            directory = DirectoryPageFactory(parent=home_page, title="Directory")
            directory.save()

        InstancesButtonFactory(
            page=home_page,
            link=directory,
            text='See all SecureDrop instances in the directory',
        )
        for i in range(number_of_instances):
            instance = DirectoryEntryFactory(parent=directory)
            if i % 3 == 0:
                scan = ScanResultFactory(
                    securedrop=instance,
                    landing_page_url=instance.landing_page_url,
                    no_failures=True,
                )
                HomePageInstancesFactory(page=home_page, instance=instance)
            elif i % 3 == 1:
                scan = ScanResultFactory(
                    securedrop=instance,
                    landing_page_url=instance.landing_page_url,
                    severe_warning=True,
                )
            else:
                scan = ScanResultFactory(
                    securedrop=instance,
                    landing_page_url=instance.landing_page_url,
                    moderate_warning=True,
                )
            scan.save()
            instance.save()
