from django.contrib import admin

from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id',
    ]
    search_fields = [
        'id',
    ]
