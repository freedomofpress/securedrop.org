from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.migrations.recorder import MigrationRecorder


OUR_APPS = [
    'blog',
    'common',
    'directory',
    'forms',
    'github',
    'home',
    'landing_page_checker',
    'marketing',
    'menus',
    'search',
    'simple',
]


class Command(BaseCommand):
    help = (
        'Delete all database records of migrations for securedrop.org-specific '
        'apps. This does not modify migration files or change the database '
        'schema; it only deletes rows from the django_migrations table.'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        count, _ = MigrationRecorder.Migration.objects.filter(
            app__in=OUR_APPS
        ).delete()
        self.stdout.write('Deleted {} migration records in {} apps'.format(
            count, len(OUR_APPS)
        ))
