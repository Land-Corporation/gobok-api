import uuid
from datetime import datetime, timezone

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models.room.models import Room
from api.models.room_image.models import RoomImage
from core.permissions import IsRoomOwnerOrReadOnly, IsRoomPropOwnerOrReadyOnly
from core.utils import process_image_data_from_request, convert_image_to_thumbnail
from infra.gcloud_storage import GCloudStorage
from .serializers import (
    RoomDefaultViewSerializer,
    RoomDetailViewSerializer,
    RoomListViewSerializer,
    OnCreateRoomImageSerializer,
    PostCreateRoomImageSerializer
)

gcs = GCloudStorage()


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().filter(is_public=True)
    serializer_class = RoomDefaultViewSerializer
    lookup_url_kwarg = 'room_id'
    permission_classes = (IsAuthenticated & IsRoomOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return RoomListViewSerializer
        if self.action == 'retrieve':
            return RoomDetailViewSerializer
        return RoomDefaultViewSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 200,
                         'array': serializer.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(self.get_queryset(), id=room_id)

        # count hit and record
        hit_count = HitCount.objects.get_for_object(room)
        HitCountMixin.hit_count(request, hit_count)

        # check whether room's owner is requester
        room.is_mine = room.user == request.user

        serializer = self.get_serializer(room)
        return Response({'status': 200,
                         'data': serializer.data}, status=status.HTTP_200_OK)

    @transaction.atomic  # ensure db rollback
    def create(self, request, *args, **kwargs):
        # create room
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            room = self.perform_create(serializer)
        except ValidationError as e:
            return Response({'status': 403,
                             'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        return Response({'status': 200,
                         'detail': f'created room',
                         'data': {'room_id': room.id}}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """A hook that is called after serializer.is_valid() and before serializer.save()"""
        instance = serializer.save(user=self.request.user)
        return instance

    def update(self, request, *args, **kwargs):
        room = self.get_object()  # performs check_object_permission
        serializer = self.get_serializer(room, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'status': 200,
                         'detail': 'updated room info'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        room = self.get_object()  # performs check_object_permission
        if not room.is_public:
            return Response({'status': 400,
                             'detail': f'room(id={room.id}) already deleted'},
                            status=status.HTTP_400_BAD_REQUEST)
        room.is_public = False
        room.save(update_fields=['is_public'])
        return Response({'status': 200,
                         'detail': f'deleted room(id={room.id})'},
                        status=status.HTTP_200_OK)


class RoomBumpViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().filter(is_public=True)
    serializer_class = RoomDefaultViewSerializer
    lookup_url_kwarg = 'room_id'
    permission_classes = (IsAuthenticated & IsRoomOwnerOrReadOnly,)

    def bump(self, request, *args, **kwargs):
        room = self.get_object()  # performs check_object_permission
        now_time = datetime.now(timezone.utc)
        time_elapsed = int((now_time - room.bumped_at).total_seconds())

        # check if able to bump
        if time_elapsed < settings.BUMP_CYCLE_SEC:
            # remaining_time = settings.BUMP_CYCLE_SEC - time_elapsed
            return Response({'status': 403,
                             'detail': f'끌올은 하루에 한번만 하실 수 있어요!⏱'},
                            status=status.HTTP_403_FORBIDDEN)
        room.bumped_at = now_time
        room.save(update_fields=['bumped_at'])
        return Response({'status': 200,
                         'detail': f'bumped room(id={room.id})'}, status=status.HTTP_200_OK)


class RoomImageViewSet(viewsets.ModelViewSet):
    """ Uploads given image file to Google Cloud Storage and
    returns accessible public url for downloading. """
    parser_classes = (MultiPartParser, JSONParser)
    queryset = RoomImage.objects.all().filter(is_public=True)
    lookup_url_kwarg = 'image_id'
    permission_classes = (IsAuthenticated, IsRoomPropOwnerOrReadyOnly,)

    def create(self, request, *args, **kwargs):
        # process image file sent
        try:
            image_bytes = process_image_data_from_request(request)
        except FileNotFoundError:
            return Response({'status': 400,
                             'detail': 'send request with image file'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Upload all to GCS
        image_filename = uuid.uuid4().hex  # use uuid4 for randomness
        gcs.upload_image_from_bytes(image_filename, image_bytes, make_public=True)

        # create thumbnail and upload to GCS
        thumbnail_bytes = convert_image_to_thumbnail(image_bytes)
        gcs.upload_image_from_bytes(f'{image_filename}{settings.THUMBNAIL_URL_SUFFIX}',
                                    thumbnail_bytes, make_public=True)

        # get public url
        public_url = gcs.get_image_public_access_url(image_filename)

        # case1) requested AFTER room creation
        data = {'url': public_url}
        # if '<room_id>' in url path
        # meaning, creating image in room edit page etc
        if 'room_id' in self.kwargs:
            room_id = self.kwargs.get('room_id', None)

            # check object permission
            self.check_object_permissions(request, Room.objects.get(id=room_id))

            # serialize
            data['room_id'] = room_id
            serializer = PostCreateRoomImageSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        # case2) requested BEFORE room creation
        else:
            serializer = OnCreateRoomImageSerializer(data=data)
            serializer.is_valid(raise_exception=True)

        return Response({'status': 200,
                         'data': serializer.data}, status=status.HTTP_200_OK)

    def reorder(self, request, *args, **kwargs):
        image_id_order = request.data.get('image_id_order', None)
        if not image_id_order:
            return Response({'status': 400,
                             'detail': 'send list of image_ids by order desired'},
                            status=status.HTTP_400_BAD_REQUEST)
        room = Room.objects.get(id=self.kwargs['room_id'])

        # check permission
        self.check_object_permissions(request, room)

        # reorder
        room.set_roomimage_order(image_id_order)
        return Response({'status': 200,
                         'detail': 'reordered room images'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        image = self.get_object()  # performs check_object_permission
        image.is_public = False
        image.save(update_fields=['is_public'])
        return Response({'status': 200,
                         'detail': 'deleted image'}, status=status.HTTP_200_OK)
