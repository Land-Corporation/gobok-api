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

    def to_internal_value(self, data):
        """ Accept unvalidated data and return validated """
        image_urls = data.get('image_urls')
        data['image_urls'] = [url for url in image_urls]
        return data

    def create(self, validated_data):
        # parse data
        user = validated_data.get('user')
        image_urls = validated_data.pop('image_urls')

        # ONLY one USER can create ONE ROOM (public)
        queryset = Room.objects.filter(user=user, is_public=True)
        if queryset.exists():
            raise ValidationError('You have already created a room.')
        room = Room.objects.create(**validated_data)
        # link room with room_image
        for url in image_urls:
            RoomImage.objects.create(room=room, url=url)
        return room

    class Meta:
        model = Room
        fields = ['title', 'content', 'published_at', 'images']
