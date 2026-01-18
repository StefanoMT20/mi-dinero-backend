from django.contrib import admin
from .models import CreditCard, Expense


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'last_four_digits', 'limit', 'used', 'created_at']
    list_filter = ['color', 'created_at', 'user']
    search_fields = ['name', 'last_four_digits']
    readonly_fields = ['id', 'used', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'user', 'amount', 'category', 'credit_card', 'date', 'created_at']
    list_filter = ['category', 'credit_card', 'date', 'created_at', 'user']
    search_fields = ['description']
    readonly_fields = ['id', 'created_at']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
