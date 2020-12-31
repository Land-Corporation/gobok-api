from django.urls import path

from .views import EmailCodeViewSet

urlpatterns = [
    path('code', EmailCodeViewSet.as_view({'post': 'create'}), name='code'),
    # path('login', LoginViewSet.as_view({'post': 'create'}), name='login'),
    # path('logout', LogoutViewSet.as_view({'post': 'create'}), name='logout'),
]
