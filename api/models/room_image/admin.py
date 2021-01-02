from django.contrib import admin

from .models import RoomImage


@admin.register(RoomImage)
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
