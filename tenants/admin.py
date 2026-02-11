from django.contrib import admin
from .models import Tenant, Company


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'created_at')
    search_fields = ('name',)
    list_filter = ('tenant',)
    readonly_fields = ('id', 'created_at', 'updated_at')
