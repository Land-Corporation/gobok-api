from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id',
        'email',
        'last_login',
        'created',
        'modified',
        'is_active',
        'is_admin'
    ]
    search_fields = [
        'id',
        'email',
    ]
