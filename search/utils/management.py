from search.models import SearchDocument


def flush_documents_by_type(result_type):
    SearchDocument.objects.filter(result_type=result_type).delete()
