from django.contrib import admin

from .models import VerificationCode


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = [
        'id',
        'code',
        'expires_at',
        'created',
        'modified'
    ]
    search_fields = [
        'id',
        'code',
    ]
