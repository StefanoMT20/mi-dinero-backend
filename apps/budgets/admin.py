from django.contrib import admin
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'period', 'start_date', 'created_at']
    list_filter = ['category', 'period']
    search_fields = ['user__email', 'category']
    ordering = ['user', 'category']
