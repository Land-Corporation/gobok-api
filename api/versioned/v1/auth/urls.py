from django.urls import path

from .views import VerificationCodeViewSet

urlpatterns = [
    path('code', VerificationCodeViewSet.as_view({'post': 'send_code'}), name='code'),
    # path('login', LoginViewSet.as_view({'post': 'create'}), name='login'),
    # path('logout', LogoutViewSet.as_view({'post': 'create'}), name='logout'),
]
