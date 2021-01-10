"""Land App API URL Configuration
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from api.services._warmup import urls as warmup_urls
from api.services.auth import urls as auth_urls
from api.services.my import urls as my_urls
from api.services.room import urls as room_urls

V = settings.API_VERSION

urlpatterns = [
    path('admin/', admin.site.urls),
    path('_ah/warmup', include(warmup_urls)),  # appengine warmup handler
    path(f'{V}/auth', include(auth_urls)),
    path(f'{V}/rooms', include(room_urls)),
    path(f'{V}/my', include(my_urls)),
]
