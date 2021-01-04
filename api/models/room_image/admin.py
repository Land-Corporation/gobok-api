from django.contrib import admin

from .models import RoomImage


@admin.register(RoomImage)
class RoomPhotoAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id',
        'room',
        'url',
        '_order',
        'is_public',
        'created',
        'modified'
    ]
    search_fields = [
        'id',
        'room',
        'url',
    ]
