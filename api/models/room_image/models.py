from django.db import models
from model_utils.models import TimeStampedModel

from api.models.room.models import Room


class RoomImage(TimeStampedModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    # Note that you need to call s3_storage.url(filename) to generate
    # pre-signed url for image asset. This is the feature AWS S3 enforces
    # us to do. There is no indefinite public url.
    filename = models.CharField(max_length=500, null=False, blank=False)
    is_public = models.BooleanField(default=True)

    class Meta:
        order_with_respect_to = 'room'
