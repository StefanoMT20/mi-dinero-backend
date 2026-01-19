import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class BankAccount(models.Model):
    """Modelo para cuentas bancarias."""

    CURRENCY_CHOICES = [
        ('PEN', 'Soles'),
        ('USD', 'Dólares'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bank_accounts',
        verbose_name='Usuario'
    )
    name = models.CharField('Nombre', max_length=100)
    balance = models.DecimalField(
        'Balance',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    last_four_digits = models.CharField(
        'Últimos 4 dígitos',
        max_length=4,
        blank=True,
        null=True
    )
    currency = models.CharField(
        'Moneda',
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='PEN'
    )
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Cuenta bancaria'
        verbose_name_plural = 'Cuentas bancarias'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class CreditCard(models.Model):
    """Modelo para tarjetas de crédito."""

    COLOR_CHOICES = [
        ('gradient1', 'Gradiente 1'),
        ('gradient2', 'Gradiente 2'),
        ('gradient3', 'Gradiente 3'),
    ]

    CURRENCY_CHOICES = [
        ('PEN', 'Soles'),
        ('USD', 'Dólares'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_cards',
        verbose_name='Usuario'
    )
    name = models.CharField('Nombre', max_length=100)
    last_four_digits = models.CharField('Últimos 4 dígitos', max_length=4)
    limit = models.DecimalField(
        'Límite de crédito',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        'Moneda de la línea',
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='PEN',
        help_text='Moneda en la que está expresado el límite de crédito'
    )
    used_pen = models.DecimalField(
        'Consumo en soles',
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    used_usd = models.DecimalField(
        'Consumo en dólares',
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    color = models.CharField('Color', max_length=20, choices=COLOR_CHOICES, default='gradient1')
    cut_off_date = models.PositiveSmallIntegerField(
        'Fecha de corte',
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )
    payment_date = models.PositiveSmallIntegerField(
        'Fecha de pago',
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Tarjeta de crédito'
        verbose_name_plural = 'Tarjetas de crédito'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (*{self.last_four_digits})"


class Expense(models.Model):
    """Modelo para gastos."""

    CURRENCY_CHOICES = [
        ('PEN', 'Soles'),
        ('USD', 'Dólares'),
    ]

    CATEGORY_CHOICES = [
        ('food', 'Comida'),
        ('transport', 'Transporte'),
        ('entertainment', 'Entretenimiento'),
        ('shopping', 'Compras'),
        ('bills', 'Servicios'),
        ('health', 'Salud'),
        ('other', 'Otros'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses',
        verbose_name='Usuario'
    )
    amount = models.DecimalField(
        'Monto',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    currency = models.CharField(
        'Moneda',
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='PEN'
    )
    category = models.CharField('Categoría', max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField('Descripción', max_length=255)
    date = models.DateField('Fecha del gasto')
    credit_card = models.ForeignKey(
        CreditCard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        verbose_name='Tarjeta de crédito'
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses',
        verbose_name='Cuenta bancaria'
    )
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['-date', '-created_at']

    def __str__(self):
        symbol = 'S/' if self.currency == 'PEN' else '$'
        return f"{self.description} - {symbol} {self.amount}"

    def save(self, *args, **kwargs):
        """Actualiza el monto usado de la tarjeta al guardar."""
        is_new = self._state.adding
        old_instance = None

        if not is_new:
            old_instance = Expense.objects.filter(pk=self.pk).first()

        super().save(*args, **kwargs)

        # Revertir el impacto en la tarjeta anterior si cambió
        if old_instance and old_instance.credit_card:
            if old_instance.credit_card != self.credit_card or old_instance.currency != self.currency or old_instance.amount != self.amount:
                self._update_card_used_amount(old_instance.credit_card)

        # Aplicar el impacto en la tarjeta actual
        if self.credit_card:
            self._update_card_used_amount(self.credit_card)

    def delete(self, *args, **kwargs):
        """Actualiza el monto usado de la tarjeta al eliminar."""
        card = self.credit_card
        super().delete(*args, **kwargs)
        if card:
            self._update_card_used_amount(card)

    def _update_card_used_amount(self, card):
        """Recalcula el monto usado de una tarjeta separado por moneda."""
        from django.db.models import Sum

        totals = card.expenses.values('currency').annotate(total=Sum('amount'))

        used_pen = 0
        used_usd = 0

        for item in totals:
            if item['currency'] == 'PEN':
                used_pen = item['total'] or 0
            elif item['currency'] == 'USD':
                used_usd = item['total'] or 0

        card.used_pen = used_pen
        card.used_usd = used_usd
        card.save(update_fields=['used_pen', 'used_usd', 'updated_at'])
