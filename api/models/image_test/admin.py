from django.contrib import admin

from .models import ImageTest


@admin.register(ImageTest)
class ImageTestAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id',
        'upload',
    ]
    search_fields = [
        'id',
    ]
