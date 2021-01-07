"""Land App API URL Configuration
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from api.services.auth import urls as auth_urls
from api.services.my import urls as my_urls
from api.services.room import urls as room_urls

V = settings.API_VERSION

urlpatterns = [
    # ELB healthcheck handler
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    # APIs
    path('admin/', admin.site.urls),
    path(f'{V}/auth/', include(auth_urls)),
    path(f'{V}/rooms/', include(room_urls)),
    path(f'{V}/my/', include(my_urls)),
]
