from django.contrib import admin
from .models import Installment


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = [
        'description',
        'user',
        'credit_card',
        'total_amount',
        'currency',
        'current_installment',
        'total_installments',
        'is_active',
        'start_date',
        'created_at',
    ]
    list_filter = ['is_active', 'currency', 'created_at']
    search_fields = ['description', 'credit_card__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
