from django.urls import path
from .views import RoomViewSet

urlpatterns = [
    path('', RoomViewSet.as_view({'get': 'list',
                                  'post': 'create'})),
    path('<room_id>', RoomViewSet.as_view({'get': 'retrieve',
                                           'put': 'update',
                                           'delete': 'delete'})),
    path('<room_id>/refresh', RoomViewSet.as_view({'post': 'refresh'})),
]
