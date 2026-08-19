from .csp import CSPCompatibleRouter
from .viewsets import DirectoryEntriesViewSet


api_router = CSPCompatibleRouter("directoryapi")
api_router.register("directory", DirectoryEntriesViewSet)
