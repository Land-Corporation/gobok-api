from django.urls import path

from .views import (
    VersionViewSet,
)

urlpatterns = [
    path('', VersionViewSet.as_view({'get': 'retrieve'})),
]
