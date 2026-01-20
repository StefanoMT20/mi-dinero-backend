import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models


class Installment(models.Model):
    """Modelo para cuotas de compras a plazos."""

    class Currency(models.TextChoices):
        PEN = 'PEN', 'Soles'
        USD = 'USD', 'Dólares'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='installments',
        verbose_name='Usuario'
    )
    credit_card = models.ForeignKey(
        'finances.CreditCard',
        on_delete=models.CASCADE,
        related_name='installments',
        verbose_name='Tarjeta de crédito'
    )
    description = models.CharField('Descripción', max_length=255)
    total_amount = models.DecimalField(
        'Monto total',
        max_digits=10,
        decimal_places=2
    )
    currency = models.CharField(
        'Moneda',
        max_length=3,
        choices=Currency.choices,
        default=Currency.PEN
    )
    total_installments = models.PositiveIntegerField('Total de cuotas')
    current_installment = models.PositiveIntegerField(
        'Cuota actual',
        default=1
    )
    start_date = models.DateField('Fecha de primera cuota')
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.description} - {self.current_installment}/{self.total_installments}"

    @property
    def monthly_amount(self) -> Decimal:
        """Calcula el monto mensual de la cuota."""
        if self.total_installments > 0:
            return (self.total_amount / self.total_installments).quantize(Decimal('0.01'))
        return Decimal('0.00')

    @property
    def remaining_amount(self) -> Decimal:
        """Calcula el monto restante por pagar."""
        remaining_installments = self.total_installments - self.current_installment + 1
        return (self.monthly_amount * remaining_installments).quantize(Decimal('0.01'))
