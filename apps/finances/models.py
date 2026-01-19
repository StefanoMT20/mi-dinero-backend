import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class BankAccount(models.Model):
    """Modelo para cuentas bancarias."""

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
    used = models.DecimalField(
        'Monto utilizado',
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

    @property
    def available(self):
        """Calcula el monto disponible."""
        return self.limit - self.used


class Expense(models.Model):
    """Modelo para gastos."""

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
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description} - S/. {self.amount}"

    def save(self, *args, **kwargs):
        """Actualiza el monto usado de la tarjeta al guardar."""
        is_new = self._state.adding
        old_instance = None

        if not is_new:
            old_instance = Expense.objects.filter(pk=self.pk).first()

        super().save(*args, **kwargs)

        if old_instance and old_instance.credit_card and old_instance.credit_card != self.credit_card:
            self._update_card_used_amount(old_instance.credit_card)

        if self.credit_card:
            self._update_card_used_amount(self.credit_card)

    def delete(self, *args, **kwargs):
        """Actualiza el monto usado de la tarjeta al eliminar."""
        card = self.credit_card
        super().delete(*args, **kwargs)
        if card:
            self._update_card_used_amount(card)

    def _update_card_used_amount(self, card):
        """Recalcula el monto usado de una tarjeta."""
        from django.db.models import Sum
        total = card.expenses.aggregate(total=Sum('amount'))['total'] or 0
        card.used = total
        card.save(update_fields=['used', 'updated_at'])
