from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from model_utils.models import TimeStampedModel

from .managers import UserManager


class User(AbstractBaseUser, TimeStampedModel, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
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
