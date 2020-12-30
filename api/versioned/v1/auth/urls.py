from django.urls import path

from .views import VerificationCodeViewSet, LoginViewSet, LogoutViewSet

urlpatterns = [
    path('code', VerificationCodeViewSet.as_view({'post': 'create'}), name='code'),
    path('login', LoginViewSet.as_view({'post': 'create'}), name='login'),
    path('logout', LogoutViewSet.as_view({'post': 'create'}), name='logout'),
]
