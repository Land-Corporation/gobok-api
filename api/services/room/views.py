import uuid
from datetime import datetime, timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from api.models.room.models import Room
from api.models.room_image.models import RoomImage
from core.processors import process_image_data_from_request
from infra.gcloud_storage import GCloudStorage
from .serializers import (
    RoomSerializer,
    OnCreateRoomImageSerializer,
    PostCreateRoomImageSerializer
)

gcs = GCloudStorage()


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_url_kwarg = 'room_id'

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(self.get_queryset(), id=room_id)
        serializer = self.get_serializer(room)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    @transaction.atomic  # ensure db rollback
    def create(self, request, *args, **kwargs):
        # create room
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            room = self.perform_create(serializer)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        return Response({'detail': f'created room(id={room.id})'}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """A hook that is called after serializer.is_valid() and before serializer.save()"""
        instance = serializer.save(user=self.request.user)
        return instance

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'detail': 'updated room info'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        room = self.get_object()
        if not room.is_public:
            return Response({'detail': f'room(id={room.id}) already deleted'},
                            status=status.HTTP_400_BAD_REQUEST)
        room.is_public = False
        room.save(update_fields=['is_public'])
        return Response({'detail': f'deleted room(id={room.id})'},
                        status=status.HTTP_200_OK)


class RoomBumpViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_url_kwarg = 'room_id'

    def bump(self, request, *args, **kwargs):
        room = self.get_object()
        now_time = datetime.now(timezone.utc)
        time_elapsed = (now_time - room.bumped_at).seconds

        # check if able to bump
        if time_elapsed < settings.POST_BUMP_CYCLE_SEC:
            remaining_time = settings.POST_BUMP_CYCLE_SEC - time_elapsed
            return Response({'detail': f'bump cycle for room(id={room.id}) not reached. '
                                       f'please wait {remaining_time}sec'},
                            status=status.HTTP_403_FORBIDDEN)
        room.bumped_at = now_time
        room.save(update_fields=['bumped_at'])
        return Response({'detail': f'bumped room(id={room.id})'}, status=status.HTTP_200_OK)


class RoomImageViewSet(viewsets.ModelViewSet):
    """ Uploads given image file to Google Cloud Storage and
    returns accessible public url for downloading. """
    parser_classes = (MultiPartParser,)
    queryset = RoomImage.objects.all()
    serializer_class = OnCreateRoomImageSerializer
    lookup_field = 'image_id'

    def create(self, request, *args, **kwargs):
        # process image file sent
        try:
            image_bytes = process_image_data_from_request(request)
        except FileNotFoundError:
            return Response({'detail': 'send request with image file'},
                            status=status.HTTP_400_BAD_REQUEST)

        # upload to GCS and get public url
        image_filename = uuid.uuid4().hex  # use uuid4 for randomness
        gcs.upload_image_from_bytes(image_filename, image_bytes, make_public=True)
        public_url = gcs.get_image_public_access_url(image_filename)

        # case1) requested AFTER room creation
        data = {'url': public_url}
        if 'room_id' in self.kwargs:  # if '<room_id>' in url path
            data['room_id'] = self.kwargs.get('room_id', None)
            serializer = PostCreateRoomImageSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        # case2) requested BEFORE room creation
        else:
            serializer = OnCreateRoomImageSerializer(data=data)
            serializer.is_valid(raise_exception=True)

        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def reorder(self, request, *args, **kwargs):
        room_id = self.kwargs.get('room_id', None)
        if not room_id:
            return Response({'detail': 'please specify room_id'},
                            status=status.HTTP_400_BAD_REQUEST)
        room = Room.objects.get(id=room_id)
        # reorder
        # TODO
        return Response({'detail': 'reordered room images'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        image = self.get_object()
        image.is_public = False
        image.save(update_fields=['is_public'])
        return Response({'detail': 'deleted image'}, status=status.HTTP_200_OK)
