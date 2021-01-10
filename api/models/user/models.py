import random
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import MinLengthValidator
from django.db import models
from model_utils.models import TimeStampedModel
from model_utils.models import TimeStampedModel

from .managers import UserManager


def generate_code() -> str:
    """Verification Code to validate user email"""
    # ex) 0234, 1322, 9211
    return f'{random.randrange(1, 10 ** settings.EMAIL_CODE_DIGIT):0{settings.EMAIL_CODE_DIGIT}}'


def get_expires_at():
    return datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_CODE_LIFETIME_MIN)


class User(AbstractBaseUser, TimeStampedModel, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    nickname = models.CharField(max_length=255)

    # Verification code related
    code = models.CharField(max_length=settings.EMAIL_CODE_DIGIT,
                            default=generate_code,
                            validators=[MinLengthValidator(settings.EMAIL_CODE_DIGIT)])
    code_expires_at = models.DateTimeField(default=get_expires_at)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Sends an email to this User"""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """"Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def email_code(self, subject, message, from_email=None, **kwargs):
        """Send Verification code to email"""
        send_mail(subject, message, from_email, [self.email], **kwargs)
