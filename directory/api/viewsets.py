from rest_framework.viewsets import ReadOnlyModelViewSet

from directory.models.entry import DirectoryEntry

from .csp import CSPCompatibleViewSetMixin
from .serializers import DirectoryEntrySerializer


class DirectoryEntriesViewSet(CSPCompatibleViewSetMixin, ReadOnlyModelViewSet):
    serializer_class = DirectoryEntrySerializer
    queryset = DirectoryEntry.objects.listed().live()
