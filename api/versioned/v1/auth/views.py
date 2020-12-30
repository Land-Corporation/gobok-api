from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from api.base.code.models import VerificationCode


class VerificationCodeViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        """ Generate Verification Code and send this code to target Email """
        email = request.data.get('email', None)
        if not email:
            return Response(data='Please provide email', status=status.HTTP_400_BAD_REQUEST)

        vc = VerificationCode.objects.create(email_to_verify=email)
        vc.email_code(from_email='jin@landcorp.io')
        return Response(status=status.HTTP_200_OK)


class LoginViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


class LogoutViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
