from django.db import models
from model_utils.models import TimeStampedModel


class ImageTest(TimeStampedModel):
    upload = models.FileField()
