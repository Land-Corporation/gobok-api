from django.urls import path

from .views import WarmUpViewSet

urlpatterns = [
    path('', WarmUpViewSet.as_view())
]
