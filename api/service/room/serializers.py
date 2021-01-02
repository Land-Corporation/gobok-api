from rest_framework import serializers
from api.model.room.models import Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['title', 'content', 'published_at']
