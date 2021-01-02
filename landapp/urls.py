"""Land App API URL Configuration
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from api.services.auth import urls as auth_urls
from api.services.room import urls as room_urls

V = settings.API_VERSION

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'{V}/auth/', include(auth_urls)),
    path(f'{V}/rooms/', include(room_urls))
]

if settings.DEBUG:
    title = 'Land App API'
    api_version = V
    sv = schema_view = get_schema_view(
        openapi.Info(
            title=title,
            default_version=api_version,
            description=f"Land App API list",
            terms_of_service='https://www.google.com/policies/terms/',
            contact=openapi.Contact(email='jin@landcorp.io'),
            license=openapi.License(name="Land Corporation License"),
        ),
        permission_classes=(permissions.AllowAny,),
    )
    urlpatterns.extend([
        url(r'^' + f'{api_version}' + '/swagger/(?P<format>\.json|\.yaml)$', sv.without_ui(cache_timeout=300)),
        url(r'^' + f'{api_version}' + '/swagger/$', sv.with_ui('swagger', cache_timeout=300)),
        url(r'^' + f'{api_version}' + '/redoc/$', sv.with_ui('redoc', cache_timeout=300)),
    ])
