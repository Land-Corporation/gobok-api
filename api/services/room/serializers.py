from django.conf import settings
from django.core.exceptions import ValidationError
from hitcount.models import HitCount
from rest_framework import serializers

from api.models.room.models import Room
from api.models.room_image.models import RoomImage


# ----------------------
# |  Nested Serializer |
# ----------------------

class OnCreateRoomImageSerializer(serializers.ModelSerializer):
    """ Room Image serializer onCreate Room. Note that this serializer CANNOT
    accept `room_id` since it is operated BEFORE room is created. """

    class Meta:
        model = RoomImage
        fields = ['id', 'url']


class PostCreateRoomImageSerializer(serializers.ModelSerializer):
    """ Room Image serializer postCreate Room. Note that this serializer CAN
        accept `room_id` since it is operated AFTER room is created. """
    room_id = serializers.IntegerField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('room_id')
        return ret

    def create(self, validated_data):
        room_id = validated_data.get('room_id')
        url = validated_data.get('url')
        room = Room.objects.get(id=room_id)
        room_image = RoomImage.objects.create(room=room, url=url)
        return room_image

    class Meta:
        model = RoomImage
        fields = ['id', 'room_id', 'url']


class ThumbnailImageSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        # add thumbnail url suffix
        ret = super().to_representation(instance)
        ret['url'] = f"{ret['url']}{settings.THUMBNAIL_URL_SUFFIX}"
        return ret

    class Meta:
        model = RoomImage
        fields = ['url']


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
            url = image.get('url', None)
            if not url:
                continue
            RoomImage.objects.create(room=room, url=url)
        return room

    class Meta:
        model = Room
        fields = ['id', 'title', 'content', 'bumped_at', 'images']


class RoomDetailViewSerializer(serializers.ModelSerializer):
    images = serializers.ListField(read_only=True)
    nickname = serializers.CharField(read_only=True)
    view_count = serializers.IntegerField(read_only=True)
    is_mine = serializers.BooleanField(default=False)

    def to_representation(self, instance):
        room_images = RoomImage.objects.filter(room=instance, is_public=True)
        # inject required fields
        instance.images = OnCreateRoomImageSerializer(room_images, many=True).data
        # only show first two letters (ch****)
        instance.nickname = f'{instance.user.nickname[:2]}****'
        instance.view_count = HitCount.objects.get_for_object(instance).hits
        return super().to_representation(instance)

    class Meta:
        model = Room
        fields = ['id', 'nickname', 'title', 'content',
                  'view_count', 'is_mine', 'bumped_at', 'images']


class MyRoomDetailViewSerializer(RoomDetailViewSerializer):
    is_mine = serializers.BooleanField(default=True)


class RoomListViewSerializer(serializers.ModelSerializer):
    thumbnail = ThumbnailImageSerializer()  # only one thumbnail image
    view_count = serializers.IntegerField(read_only=True)

    def to_representation(self, instance):
        room_images = RoomImage.objects.filter(room=instance, is_public=True)
        instance.thumbnail = room_images[0] if room_images else None
        instance.view_count = HitCount.objects.get_for_object(instance).hits
        return super().to_representation(instance)

    class Meta:
        model = Room
        # TODO: add field 'view_count' ...
        fields = ['id', 'title', 'view_count', 'bumped_at', 'thumbnail']
