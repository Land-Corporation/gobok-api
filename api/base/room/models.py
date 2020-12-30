from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class Room(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=250, null=False, blank=False)
    content = models.TextField(null=False, blank=False)
    published_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
