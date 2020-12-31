from django.core.validators import validate_email
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from api.base.user.models import User, generate_code, get_expires_at
from .serializers import EmailCodeSerializer, UserLoginSerializer


class EmailCodeViewSet(viewsets.ModelViewSet):
    serializer_class = EmailCodeSerializer

    def create(self, request, *args, **kwargs):

        """ Generate Verification Code and send this code to target Email """
        email = self.request.data.get('email', None)

        if not email:
            return Response(data='Please provide email info', status=status.HTTP_400_BAD_REQUEST)

        validate_email(email)
        try:
            user = User.objects.get(email=email)
            user.code = generate_code()  # reset code
            user.code_expires_at = get_expires_at()
            user.save(update_fields=['code', 'code_expires_at'])
        except User.DoesNotExist:
            user = User.objects.create_user(email=email)

        subject = f'[고대복덕방] 인증코드입니다.'
        message = f'인증코드입니다: {user.code}'
        user.email_code(subject, message)

        return Response(status=status.HTTP_200_OK)


class LoginViewSet(viewsets.ModelViewSet):
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):


        return Response(status=status.HTTP_200_OK)


class LogoutViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
