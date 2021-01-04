from django.urls import path

from .views import (
    MyRoomViewSet,
    MyFeedbackViewSet
)

urlpatterns = [
    path('rooms', MyRoomViewSet.as_view({'get': 'list'})),
    path('feedback', MyFeedbackViewSet.as_view({'post': 'create'})),
]
