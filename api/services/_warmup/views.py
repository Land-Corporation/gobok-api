from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class WarmUpViewSet(APIView):
    """
    A simple ViewSet for GAE warmup handler
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        return Response(status=status.HTTP_200_OK)
