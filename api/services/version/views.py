from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from api.models.version.models import Version
from .serializers import VersionViewSerializer


class VersionViewSet(viewsets.ModelViewSet):
    serializer_class = VersionViewSerializer

    def retrieve(self, request, *args, **kwargs):
        queryset = Version.objects.latest('id')
        serializer = self.get_serializer(queryset)
        return Response({'status': 200,
                         'data': serializer.data}, status=status.HTTP_200_OK)
