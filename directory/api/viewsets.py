from rest_framework.viewsets import ReadOnlyModelViewSet

from directory.models.entry import DirectoryEntry

from .serializers import DirectoryEntrySerializer


class DirectoryEntriesViewSet(ReadOnlyModelViewSet):
    serializer_class = DirectoryEntrySerializer
    queryset = DirectoryEntry.objects.live()
