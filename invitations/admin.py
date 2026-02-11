from django.contrib import admin
from .models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'tenant', 'expires_at', 'used_at', 'created_at')
    search_fields = ('email',)
    list_filter = ('role', 'tenant')
    readonly_fields = ('id', 'token', 'created_at', 'updated_at')
