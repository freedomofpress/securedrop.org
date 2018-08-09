import argparse

from django.core.management.base import BaseCommand

from directory.models.entry import DirectoryEntry
from directory.utils import scan_csv


class Command(BaseCommand):
    help = "Output a CSV of most recent scan results for all directory entries"

    def add_arguments(self, parser):
        parser.add_argument(
            '-o',
            '--output',
            dest='output',
            type=argparse.FileType('w')
        )

    def handle(self, *args, **options):
        if options['output'] is not None:
            stream = options['output']
        else:
            stream = self.stdout
        entries = DirectoryEntry.objects.all()
        output = scan_csv(entries)
        stream.write(output)
