from rest_framework.viewsets import ReadOnlyModelViewSet

from directory.models.entry import DirectoryEntry

from .serializers import DirectoryEntrySerializer
from .csp import CSPCompatibleViewSetMixin


class DirectoryEntriesViewSet(CSPCompatibleViewSetMixin, ReadOnlyModelViewSet):
    serializer_class = DirectoryEntrySerializer
    queryset = DirectoryEntry.objects.live()
