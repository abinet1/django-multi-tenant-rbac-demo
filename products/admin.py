from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'company', 'created_by', 'customer', 'created_at')
    search_fields = ('name',)
    list_filter = ('tenant', 'company')
    readonly_fields = ('id', 'share_token', 'created_at', 'updated_at')
