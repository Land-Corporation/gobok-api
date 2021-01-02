import uuid

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from api.models.room.models import Room
from api.models.room_photo.models import RoomPhoto
from core.processors import process_image_data_from_request
from infra.gcloud_storage import GCloudStorage
from .serializers import RoomSerializer

gcs = GCloudStorage()


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.object.all()
    serializer_class = RoomSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(self.get_queryset(), id=room_id)
        serializer = self.get_serializer(room)
        # TODO: get room photos as well
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # TODO: save room photo and create room_photo model as well
        #  initialize CloudStorage too.
        pass

    def update(self, request, *args, **kwargs):
        pass

    def destroy(self, request, *args, **kwargs):
        pass

    def refresh(self, request, *args, **kwargs):
        pass


class RoomImageUploadView(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser,)
    queryset = RoomPhoto.objects.all()

    def upload(self, request):
        # process image file sent
        try:
            image_bytes = process_image_data_from_request(request)
        except FileNotFoundError:
            return Response(data={'detail': 'Please send request with image file'},
                            status=status.HTTP_400_BAD_REQUEST)

        # upload to GCS
        image_filename = uuid.uuid4().hex  # use uuid4 for randomness
        # TODO: need to change make_public to False someday
        gcs.upload_image_from_bytes(image_filename, image_bytes, make_public=True)

        public_url = gcs.get_image_public_access_url(image_filename)
        return Response(data={'data': public_url}, status=status.HTTP_200_OK)

