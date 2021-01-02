import random
from datetime import datetime, timedelta, timezone

from django.core.mail import send_mail
from django.core.validators import MinLengthValidator
from django.db import models
from model_utils.models import TimeStampedModel

CODE_DIGIT = 4
CODE_LIFETIME_MIN = 10


def get_expires_at():
    return datetime.now(timezone.utc) + timedelta(minutes=CODE_LIFETIME_MIN)


def generate_code() -> str:
    # ex) 0234, 1322, 9211
    return f'{random.randrange(1, 10 ** CODE_DIGIT):0{CODE_DIGIT}}'


class VerificationCode(TimeStampedModel):
    code = models.CharField(max_length=CODE_DIGIT,
                            editable=False,
                            default=generate_code,
                            validators=[MinLengthValidator(CODE_DIGIT)])
    email_to_verify = models.EmailField(max_length=255, null=False)
    expires_at = models.DateTimeField(default=get_expires_at)

    def __str__(self):
        return self.code

    def email_code(self, from_email=None, **kwargs):
        """Send Verification code to email"""
        subject = f'Land Corporation 인증코드입니다.'
        message = f'인증코드입니다: {self.code}'
        send_mail(subject, message, from_email, [self.email_to_verify], **kwargs)
