from datetime import datetime, timezone

from django.core.validators import validate_email
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from api.models.user.models import User, generate_code, get_expires_at
from .serializers import VerificationCodeSerializer, LoginSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class VerificationCodeViewSet(viewsets.ModelViewSet):
    serializer_class = VerificationCodeSerializer

    def create(self, request, *args, **kwargs):
        """ Generate Verification Code and send this code to target Email """
        email = request.data.get('email', None)

        if not email:
            return Response(data={'detail': 'Please provide email info'},
                            status=status.HTTP_400_BAD_REQUEST)

        validate_email(email)
        try:
            user = User.objects.get(email=email)
            user.code = generate_code()  # reset code
            user.code_expires_at = get_expires_at()
            user.save(update_fields=['code', 'code_expires_at'])
        except User.DoesNotExist:
            # code will be automatically generated
            user = User.objects.create_user(email=email)

        subject = f'[고대복덕방] 인증코드입니다.'
        message = f'인증코드입니다: {user.code}'
        user.email_code(subject, message)

        return Response(status=status.HTTP_200_OK)


class LoginViewSet(viewsets.ModelViewSet):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        code = request.data.get('code', None)

        # get user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(data={'detail': 'Please request for code first.'},
                            status=status.HTTP_403_FORBIDDEN)
        # check code and expiration
        if user.code != code:
            return Response(data={'detail': 'Invalid code.'},
                            status=status.HTTP_403_FORBIDDEN)
        if user.code_expires_at < datetime.now(timezone.utc):
            return Response(data={'detail': 'Code expired.'},
                            status=status.HTTP_403_FORBIDDEN)
        # issue jwt
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        return Response(data={'data': token},
                        status=status.HTTP_200_OK)


class LogoutViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
