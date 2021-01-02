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
        'published_at',
        'created_at',
        'updated_at'
    ]
    search_fields = [
        'id',
        'user',
        'title',
        'content',
    ]
