from django.db import models
from model_utils.models import TimeStampedModel


class Version(TimeStampedModel):
    ios_min = models.CharField(max_length=120, null=False, blank=False)
    android_min = models.CharField(max_length=120, null=False, blank=False)
