from django.urls import path

from .views import RoomViewSet, RoomImageUploadView, RoomBumpViewSet

urlpatterns = [
    path('', RoomViewSet.as_view({'get': 'list',
                                  'post': 'create'})),
    path('images', RoomImageUploadView.as_view({'post': 'upload'})),
    path('<room_id>', RoomViewSet.as_view({'get': 'retrieve',
                                           'put': 'update',
                                           'delete': 'destroy'})),
    path('<room_id>/refresh', RoomBumpViewSet.as_view({'post': 'bump'})),
]
