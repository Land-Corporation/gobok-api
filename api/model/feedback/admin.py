from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id',
    ]
    search_fields = [
        'id',
    ]
