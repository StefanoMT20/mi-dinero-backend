from django.contrib import admin
from .models import BankAccount, CreditCard, Expense


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'balance', 'last_four_digits', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'last_four_digits']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'last_four_digits', 'limit', 'currency', 'used_pen', 'used_usd', 'created_at']
    list_filter = ['currency', 'color', 'created_at', 'user']
    search_fields = ['name', 'last_four_digits']
    readonly_fields = ['id', 'used_pen', 'used_usd', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'user', 'amount', 'currency', 'category', 'credit_card', 'bank_account', 'date', 'created_at']
    list_filter = ['currency', 'category', 'credit_card', 'bank_account', 'date', 'created_at', 'user']
    search_fields = ['description']
    readonly_fields = ['id', 'created_at']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
