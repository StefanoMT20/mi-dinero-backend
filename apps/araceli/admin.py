from django.contrib import admin

from .models import ClothingItem, NailService


@admin.register(NailService)
class NailServiceAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'service_type', 'price', 'cost', 'date', 'user']
    list_filter = ['service_type', 'date', 'user']
    search_fields = ['client_name', 'notes']
    readonly_fields = ['id', 'created_at']
    ordering = ['-date']


@admin.register(ClothingItem)
class ClothingItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'purchase_price', 'sale_price', 'purchase_date', 'sale_date', 'user']
    list_filter = ['status', 'category', 'purchase_date', 'user']
    search_fields = ['name', 'buyer_name', 'notes']
    readonly_fields = ['id', 'created_at']
    ordering = ['-purchase_date']
