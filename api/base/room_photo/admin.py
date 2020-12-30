from django.contrib import admin

from .models import RoomPhoto


@admin.register(RoomPhoto)
class RoomPhotoAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id',
        'room',
        'url',
        'created',
        'modified'
    ]
    search_fields = [
        'id',
        'room',
        'url',
    ]
