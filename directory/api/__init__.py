from rest_framework.routers import DefaultRouter

from .viewsets import DirectoryEntriesViewSet

api_router = DefaultRouter('directoryapi')
api_router.register('directory', DirectoryEntriesViewSet)
