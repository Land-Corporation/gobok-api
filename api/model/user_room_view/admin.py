from django.contrib import admin

from .models import UserRoomView


@admin.register(UserRoomView)
class UserRoomViewAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id',
    ]
    search_fields = [
        'id',
    ]
