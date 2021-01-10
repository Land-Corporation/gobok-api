from datetime import datetime, timezone

from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from api.models.user.models import User, generate_code, get_expires_at

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class VerificationCodeViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """ Generate Verification Code and send this code to target Email """
        email = request.data.get('email', None)

        if not email:
            return Response(data={'detail': 'Please provide email info'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            user.code = generate_code()  # reset code
            user.code_expires_at = get_expires_at()
            user.save(update_fields=['code', 'code_expires_at'])
        except User.DoesNotExist:
            # code will be automatically generated
            try:
                user = User.objects.create_user(email=email)
            # Validate only whitelisted domain
            except ValidationError as e:
                return Response({'status': 406,
                                 'detail': f'요청하신 이메일 도메인({e.message})은 지원하지 않습니다😥'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
        # send verification email
        code = user.code
        subject = f'[안암랜드] 인증코드 {code}'
        msg_html = render_to_string('email_verification.html', {'code': code})
        user.email_code(subject, '', settings.DEFAULT_FROM_EMAIL, html_message=msg_html)
        return Response({'status': 200, 'detail': '인증코드를 전송했습니다!😀'},
                        status=status.HTTP_200_OK)


class LoginViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        code = request.data.get('code', None)

        # get user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'status': 403,
                             'detail': 'Please request for code first.'},
                            status=status.HTTP_403_FORBIDDEN)

        # BYPASS_AUTH_CHECK if MASTER_KEY_EMAIL
        if email == settings.MASTER_KEY_EMAIL and code == '9999':
            return self.issue_jwt_and_return_200(user)

        # check code and expiration
        if user.code != code:
            return Response({'status': 403,
                             'detail': 'Invalid code.'},
                            status=status.HTTP_403_FORBIDDEN)
        now_time = datetime.now(timezone.utc)
        if user.code_expires_at < now_time:
            return Response({'status': 403,
                             'detail': 'Code expired.'},
                            status=status.HTTP_403_FORBIDDEN)
        # make code expired
        user.code_expires_at = now_time
        user.save(update_fields=['code_expires_at'])

        return self.issue_jwt_and_return_200(user)

    @staticmethod
    def issue_jwt_and_return_200(user):
        # issue jwt
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return Response({'status': 200,
                         'detail': 'Code verified. JWT issued.',
                         'data': token},
                        status=status.HTTP_200_OK)


class LogoutViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
