from rest_framework import serializers
from api.base.room.models import Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['title', 'content', 'published_at']
