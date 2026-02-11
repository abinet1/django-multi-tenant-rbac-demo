from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'role', 'tenant', 'company', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email',)
    list_filter = ('role', 'tenant', 'is_active', 'is_superuser')
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_login', 'date_joined')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Role & Tenant', {'fields': ('role', 'tenant', 'company')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'tenant', 'company'),
        }),
    )
