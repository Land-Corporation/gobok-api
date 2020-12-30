"""Land App API URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from api.versioned.v1.auth import urls as auth_urls


urlpatterns = [
    path('auth/', include(auth_urls)),
    path('admin/', admin.site.urls),
]
