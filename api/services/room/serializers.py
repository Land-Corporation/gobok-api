from rest_framework import serializers

from api.models.room.models import Room
from api.models.room_image.models import RoomImage
from django.core.exceptions import ValidationError


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['url']


class RoomSerializer(serializers.ModelSerializer):
    images = RoomImageSerializer(many=True)

    def to_representation(self, instance):
        room_images = RoomImage.objects.filter(room=instance)
        instance.images = RoomImageSerializer(room_images, many=True).data
        ret = super().to_representation(instance)
        return ret

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
        fields = ['title', 'content', 'published_at', 'images']
