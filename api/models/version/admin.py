from django.contrib import admin

from .models import Version


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id',
        'ios_min',
        'android_min',
    ]
    search_fields = [
        'id'
    ]
