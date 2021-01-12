from rest_framework import serializers

from api.models.version.models import Version


class VersionViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = ['ios_min', 'android_min']
