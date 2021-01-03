from django.contrib import admin

from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id',
        'user',
        'title',
        'content',
        'bumped_at',
        'is_public'
    ]
    search_fields = [
        'id',
        'user',
        'title',
        'content',
    ]
