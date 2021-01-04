from django.db import models
from model_utils.models import TimeStampedModel

from api.models.room.models import Room


class RoomImage(TimeStampedModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE,
                             related_name='room_images')
    url = models.URLField(max_length=200, null=False, blank=False)
    is_public = models.BooleanField(default=True)

    class Meta:
        order_with_respect_to = 'room'
