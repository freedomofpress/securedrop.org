from django.db import transaction
from django.core.management.base import BaseCommand

from directory.models import DirectoryPage
from directory.tests.factories import DirectoryPageFactory
from home.models import HomePage
from landing_page_checker.tests.factories import SecuredropFactory


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
            directory = DirectoryPageFactory(parent=home_page)
            directory.save()
        for _ in range(number_of_instances):
            instance = SecuredropFactory(page=directory)
            instance.save()
