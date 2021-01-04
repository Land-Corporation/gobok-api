from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id',
        'user',
        'title',
        'content'
    ]
    search_fields = [
        'id',
        'user',
        'title',
    ]
