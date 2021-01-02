from django.db import models
from model_utils.models import TimeStampedModel

from api.model.room.models import Room


class RoomPhoto(TimeStampedModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    url = models.CharField(null=False, blank=False)
