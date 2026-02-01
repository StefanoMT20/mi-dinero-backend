import uuid
from django.conf import settings
from django.db import models

from apps.categories.models import Category


class BudgetPeriod(models.TextChoices):
    WEEKLY = 'weekly', 'Semanal'
    BIWEEKLY = 'biweekly', 'Quincenal'
    MONTHLY = 'monthly', 'Mensual'


class Budget(models.Model):
    """Modelo para presupuestos por categoría."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Usuario'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Categoría'
    )
    amount = models.DecimalField(
        'Monto',
        max_digits=12,
        decimal_places=2
    )
    period = models.CharField(
        'Período',
        max_length=10,
        choices=BudgetPeriod.choices
    )
    start_date = models.DateField('Fecha de inicio')
    end_date = models.DateField('Fecha de fin', null=True, blank=True)
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        unique_together = ['user', 'category']
        ordering = ['category']

    def __str__(self):
        return f"{self.category.name} - {self.amount}"
