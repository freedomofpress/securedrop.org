from django.core.management.base import BaseCommand
from django.db import transaction

from search.utils.documentation import index_documentation_pages
from search.utils.management import flush_documents_by_type


class Command(BaseCommand):
    help = "Update the SearchDocument instances for all ReadTheDocs pages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--rebuild",
            action="store_true",
            dest="rebuild",
            default=False,
            help="Flush the search document database before updating",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["rebuild"] is True:
            flush_documents_by_type("D")

        all_results = index_documentation_pages()

        created_results = list(filter(lambda x: x[1] is True, all_results))
        updated_results = list(filter(lambda x: x[1] is False, all_results))

        created_results_count = len(created_results)
        updated_results_count = len(updated_results)

        self.stdout.write(f"- {created_results_count} SearchDocuments created")
        self.stdout.write(
            f"- {updated_results_count} SearchDocuments updated (does not necessarily indicate changes)"
        )
