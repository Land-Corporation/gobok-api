from django.urls import path

from .views import (
    UserRoomViewSet,
    UserFeedbackViewSet
)

urlpatterns = [
    path('<user_id>/rooms', UserRoomViewSet.as_view({'get': 'list'})),
    path('<user_id>/feedback', UserFeedbackViewSet.as_view({'post': 'send'})),
]
