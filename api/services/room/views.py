import uuid
from django.db import transaction

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from api.models.room.models import Room
from api.models.room_image.models import RoomImage
from core.processors import process_image_data_from_request
from infra.gcloud_storage import GCloudStorage
from .serializers import RoomSerializer

gcs = GCloudStorage()


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

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
        return Response({'detail': f'Successfully created room(id={room.id})'}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """A hook that is called after serializer.is_valid() and before serializer.save()"""
        instance = serializer.save(user=self.request.user)
        return instance

    def update(self, request, *args, **kwargs):
        pass

    def destroy(self, request, *args, **kwargs):
        pass

    def refresh(self, request, *args, **kwargs):
        pass


class RoomImageUploadView(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser,)
    queryset = RoomImage.objects.all()

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

#
# class RoomImageDownloadView(viewsets.ModelViewSet):
#     renderer_classes = [PNGRenderer]
#     queryset = Room.objects.all()
#
#     def download(self, request, *args, **kwargs):
#         location_id = self.kwargs.get('location_id')
#         if self.request.path.split('/')[-2] == 'current-map':
#             try:
#                 location = Location.objects.get(
#                     id=location_id,
#                     retired=False,
#                 )
#             except Location.DoesNotExist as e:
#                 raise exceptions.NotFound(detail=str(e))
#             found = location.current_map
#         else:
#             found = get_target_map_from_location(self)
#         # Download image data from GCS bucket
#         try:
#             image_data = storage.download_map_image(location_id,
#                                                     found.image_file_name)
#         except GCSNotFound:
#             raise exceptions.NotFound(
#                 detail='Image not found in Google Storage.')
#
#         if self.request.path.split('/')[-1] == 'base64':
#             png_file = io.BytesIO()
#             Image.open(io.BytesIO(image_data)).save(png_file, format='PNG')
#             base64_image = base64.b64encode(png_file.getvalue()).decode('UTF-8')
#             return JsonResponse({'data': base64_image})
#
#         response = Response(image_data, content_type='image/png')
#         disposition = self.request.query_params.get('disposition')
#         if disposition == 'attachment':
#             response['Content-Disposition'] = \
#                 f'attachment; filename={found.image_file_name}'
#         else:
#             response['Content-Disposition'] = 'inline'
#         return response
