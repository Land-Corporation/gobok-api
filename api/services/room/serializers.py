from django.core.exceptions import ValidationError
from hitcount.models import HitCount
from rest_framework import serializers

from api.models.room.models import Room
from api.models.room_image.models import RoomImage
from infra.s3_storage import S3ImageStorage
from django.conf import settings

# ----------------------
# |  Nested Serializer |
# ----------------------

class OnCreateRoomImageSerializer(serializers.ModelSerializer):
    """ Room Image serializer onCreate Room. Note that this serializer CANNOT
    accept `room_id` since it is operated BEFORE room is created. """

    class Meta:
        model = RoomImage
        fields = ['id', 'filename']


class PostCreateRoomImageSerializer(serializers.ModelSerializer):
    """ Room Image serializer postCreate Room. Note that this serializer CAN
        accept `room_id` since it is operated AFTER room is created. """
    room_id = serializers.IntegerField()

    def to_representation(self, instance):
        """ Should return pre-signed AWS S3 url """
        ret = super().to_representation(instance)
        filename = ret.pop('filename')
        ret['url'] = S3ImageStorage().url(filename)
        ret.pop('room_id')
        return ret

    def create(self, validated_data):
        room_id = validated_data.get('room_id')
        filename = validated_data.get('filename')
        room = Room.objects.get(id=room_id)
        room_image = RoomImage.objects.create(room=room, filename=filename)
        return room_image

    class Meta:
        model = RoomImage
        fields = ['id', 'room_id', 'filename']


class ThumbnailImageSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        # add thumbnail url suffix
        ret = super().to_representation(instance)
        thumbnail_filename = f'{ret["filename"]}/{settings.THUMBNAIL_URL_SUFFIX}'
        ret['url'] = S3ImageStorage().url(thumbnail_filename)
        return ret

    class Meta:
        model = RoomImage
        fields = ['filename']


# -----------------------
# |  ViewSet Serializer |
# -----------------------

class RoomDefaultViewSerializer(serializers.ModelSerializer):
    images = OnCreateRoomImageSerializer(many=True)

    def create(self, validated_data):
        # parse data
        user = validated_data.get('user')
        images = validated_data.pop('images')

        # ONLY one USER can create ONE ROOM (public)
        queryset = Room.objects.filter(user=user, is_public=True)
        if queryset.exists():
            raise ValidationError('You have already created a room.')
        room = Room.objects.create(**validated_data)
        # link room with room_image
        for image in images:
            filename = image.get('filename', None)
            if not filename:
                continue
            RoomImage.objects.create(room=room, filename=filename)
        return room

    class Meta:
        model = Room
        fields = ['id', 'title', 'content', 'bumped_at', 'images']


class RoomDetailViewSerializer(serializers.ModelSerializer):
    images = serializers.ListField(read_only=True)
    nickname = serializers.CharField(read_only=True)
    view_count = serializers.IntegerField(read_only=True)

    def to_representation(self, instance):
        room_images = RoomImage.objects.filter(room=instance, is_public=True)

        # inject required fields
        instance.images = OnCreateRoomImageSerializer(room_images, many=True).data
        instance.nickname = instance.user.nickname
        instance.view_count = HitCount.objects.get_for_object(instance).hits
        return super().to_representation(instance)

    class Meta:
        model = Room
        # TODO: add field 'view_count' ...
        fields = ['id', 'nickname', 'title', 'content',
                  'view_count', 'bumped_at', 'images']


class RoomListViewSerializer(serializers.ModelSerializer):
    thumbnail = ThumbnailImageSerializer()  # only one thumbnail image
    view_count = serializers.IntegerField(read_only=True)

    def to_representation(self, instance):
        instance.thumbnail = RoomImage.objects.filter(room=instance, is_public=True)[0]
        instance.view_count = HitCount.objects.get_for_object(instance).hits
        return super().to_representation(instance)

    class Meta:
        model = Room
        fields = ['id', 'title', 'view_count', 'bumped_at', 'thumbnail']
