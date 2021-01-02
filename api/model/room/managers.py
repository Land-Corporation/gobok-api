from django.db import models

from api.model.user.models import User


class RoomManager(models.Manager):
    use_in_migrations = True

    def create(self, user: User, **extra_fields):
        room = self.model(user=user, **extra_fields)
        room.full_clean()
        user.save(using=self._db)
        return user
