from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response


class UserRoomViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        return Response(data='', status=status.HTTP_200_OK)


class UserFeedbackViewSet(viewsets.ModelViewSet):
    def send(self, request, *args, **kwargs):
        return Response(data='', status=status.HTTP_200_OK)
