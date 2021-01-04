from django.urls import path

from .views import (
    RoomViewSet,
    RoomBumpViewSet,
    RoomImageViewSet,
)

urlpatterns = [
    # room data related
    path('', RoomViewSet.as_view({'get': 'list',
                                  'post': 'create'})),
    path('images', RoomImageViewSet.as_view({'post': 'create'})),
    path('images/<image_id>', RoomImageViewSet.as_view({'delete': 'destroy'})),

    path('<room_id>', RoomViewSet.as_view({'get': 'retrieve',
                                           'put': 'update',
                                           'delete': 'destroy'})),
    path('<room_id>/refresh', RoomBumpViewSet.as_view({'post': 'bump'})),  # 끌올
    path('<room_id>/images', RoomImageViewSet.as_view({'post': 'create',
                                                       'put': 'reorder'})),
]
