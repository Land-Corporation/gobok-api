import requests
from django.conf import settings
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from api.models.room.models import Room
from api.services.room.serializers import MyRoomDetailViewSerializer
from .serializers import FeedbackSerializer


class MyRoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().filter(is_public=True)
    serializer_class = MyRoomDetailViewSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 200,
                         'array': serializer.data}, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class MyFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # trigger Slack webhook
        title = serializer.data['title']
        content = serializer.data['content']
        payload = {"text": f'*작성자*: {request.user.email}\n'
                           f'*제목*: {title}\n'
                           f'*내용*: {content}'}
        requests.post(settings.SLACK_FEEDBACK_WEBHOOK_URL, json=payload)

        return Response({'status': 200,
                         'detail': 'feedback sent'}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """A hook that is called after serializer.is_valid() and before serializer.save()"""
        instance = serializer.save(user=self.request.user)
        return instance
