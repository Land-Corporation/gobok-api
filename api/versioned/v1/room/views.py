from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from api.base.room.models import Room
from .serializers import RoomSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.object.all()
    serializer_class = RoomSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        
        return

    def create(self, request, *args, **kwargs):
        pass

    def update(self, request, *args, **kwargs):
        pass

    def destroy(self, request, *args, **kwargs):
        pass

    def refresh(self, request, *args, **kwargs):
        pass
