from django.urls import path

from .views import (
    RoomViewSet,
    RoomBumpViewSet,
    RoomImageViewSet,
)

urlpatterns = [
    # room data related
    path('', RoomViewSet.as_view({'get': 'list',  # isAuthenticated
                                  'post': 'create'})),  # isAuthenticated
    path('images', RoomImageViewSet.as_view({'post': 'create'})),  # isAuthenticated

    path('<room_id>', RoomViewSet.as_view({'get': 'retrieve',  # isAuthenticated
                                           'put': 'update',  # isAuthenticated && hasRoom(objectPermission)
                                           'delete': 'destroy'})),  # isAuthenticated && hasRoom
    path('<room_id>/refresh', RoomBumpViewSet.as_view({'post': 'bump'})),  # 끌올 # isAuthenticated && hasRoom
    path('<room_id>/images', RoomImageViewSet.as_view({'post': 'create',  # isAuthenticated && hasRoom
                                                       'put': 'reorder'})),  # isAuthenticated && hasRoom
    path('<room_id>/images/<image_id>', RoomImageViewSet.as_view({'delete': 'destroy'}))  # isAuthenticated && hasRoom
]
