from .viewsets import DirectoryEntriesViewSet
from .csp import CSPCompatibleRouter

api_router = CSPCompatibleRouter('directoryapi')
api_router.register('directory', DirectoryEntriesViewSet)
