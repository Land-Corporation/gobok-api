from django.conf import settings
from rest_framework import serializers

from api.model.user.models import User


class VerificationCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ['email']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    code = serializers.CharField(max_length=settings.EMAIL_CODE_DIGIT)

    class Meta:
        model = User
        fields = ['email', 'code']
