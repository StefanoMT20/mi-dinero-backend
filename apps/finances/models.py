import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.categories.models import Category


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
    subtract_expenses = models.BooleanField(
        'Restar gastos',
        default=True,
        help_text='Si está activo, resta los gastos del saldo'
    )
    add_incomes = models.BooleanField(
        'Sumar ingresos',
        default=False,
        help_text='Si está activo, suma los ingresos al saldo'
    )
    balance_updated_at = models.DateTimeField(
        'Fecha de actualización del saldo',
        null=True,
        blank=True,
        help_text='Si tiene valor, solo gastos/ingresos creados después de esta fecha afectan el saldo'
    )
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Cuenta bancaria'
        verbose_name_plural = 'Cuentas bancarias'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    @property
    def total_income(self):
        """Calcula el total de ingresos de esta cuenta en su moneda."""
        from django.db.models import Sum
        queryset = self.incomes.filter(currency=self.currency)
        if self.balance_updated_at:
            queryset = queryset.filter(created_at__gte=self.balance_updated_at)
        total = queryset.aggregate(total=Sum('amount'))['total']
        return total or 0

    @property
    def total_expenses(self):
        """Calcula el total de gastos de esta cuenta en su moneda."""
        from django.db.models import Sum
        queryset = self.expenses.filter(currency=self.currency)
        if self.balance_updated_at:
            queryset = queryset.filter(created_at__gte=self.balance_updated_at)
        total = queryset.aggregate(total=Sum('amount'))['total']
        return total or 0

    @property
    def total_fixed_income(self):
        """Calcula el total de ingresos fijos que ya deberían haberse aplicado este mes."""
        from django.db.models import Sum
        from django.utils import timezone
        today = timezone.now().date()
        current_day = today.day

        # Sumar ingresos fijos activos cuyo día del mes ya pasó o es hoy
        total = self.fixed_incomes.filter(
            currency=self.currency,
            is_active=True,
            day_of_month__lte=current_day
        ).aggregate(total=Sum('amount'))['total']
        return total or 0

    @property
    def total_fixed_expenses(self):
        """Calcula el total de gastos fijos que ya deberían haberse aplicado este mes."""
        from django.db.models import Sum
        from django.utils import timezone
        today = timezone.now().date()
        current_day = today.day

        # Sumar gastos fijos activos cuyo día del mes ya pasó o es hoy
        total = self.fixed_expenses.filter(
            currency=self.currency,
            is_active=True,
            day_of_month__lte=current_day
        ).aggregate(total=Sum('amount'))['total']
        return total or 0

    @property
    def calculated_balance(self):
        """Calcula el balance según las opciones configuradas."""
        from decimal import Decimal
        result = Decimal(str(self.balance))
        if self.subtract_expenses:
            result -= Decimal(str(self.total_expenses))
            result -= Decimal(str(self.total_fixed_expenses))
        if self.add_incomes:
            result += Decimal(str(self.total_income))
            result += Decimal(str(self.total_fixed_income))
        return result


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
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='expenses',
        verbose_name='Categoría',
        null=True,
        blank=True
    )
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


class FixedExpense(models.Model):
    """Modelo para gastos fijos recurrentes."""

    CURRENCY_CHOICES = [
        ('PEN', 'Soles'),
        ('USD', 'Dólares'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fixed_expenses',
        verbose_name='Usuario'
    )
    name = models.CharField('Nombre', max_length=100)
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
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='fixed_expenses',
        verbose_name='Categoría',
        null=True,
        blank=True
    )
    day_of_month = models.PositiveSmallIntegerField(
        'Día del mes',
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )
    credit_card = models.ForeignKey(
        CreditCard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fixed_expenses',
        verbose_name='Tarjeta de crédito'
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fixed_expenses',
        verbose_name='Cuenta bancaria'
    )
    is_active = models.BooleanField('Activo', default=True)
    last_processed_date = models.DateField(
        'Última fecha procesada',
        null=True,
        blank=True,
        help_text='Fecha del último mes en que se convirtió a gasto real'
    )
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Gasto fijo'
        verbose_name_plural = 'Gastos fijos'
        ordering = ['day_of_month', 'name']

    def __str__(self):
        symbol = 'S/' if self.currency == 'PEN' else '$'
        return f"{self.name} - {symbol} {self.amount}"


class Income(models.Model):
    """Modelo para ingresos."""

    CURRENCY_CHOICES = [
        ('PEN', 'Soles'),
        ('USD', 'Dólares'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='incomes',
        verbose_name='Usuario'
    )
    amount = models.DecimalField(
        'Monto',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='incomes',
        verbose_name='Categoría',
        null=True,
        blank=True
    )
    description = models.CharField('Descripción', max_length=255)
    currency = models.CharField(
        'Moneda',
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='PEN'
    )
    date = models.DateField('Fecha del ingreso')
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incomes',
        verbose_name='Cuenta bancaria'
    )
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Ingreso'
        verbose_name_plural = 'Ingresos'
        ordering = ['-date', '-created_at']

    def __str__(self):
        symbol = 'S/' if self.currency == 'PEN' else '$'
        return f"{self.description} - {symbol} {self.amount}"


class FixedIncome(models.Model):
    """Modelo para ingresos fijos recurrentes."""

    CURRENCY_CHOICES = [
        ('PEN', 'Soles'),
        ('USD', 'Dólares'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fixed_incomes',
        verbose_name='Usuario'
    )
    name = models.CharField('Nombre', max_length=100)
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
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='fixed_incomes',
        verbose_name='Categoría',
        null=True,
        blank=True
    )
    day_of_month = models.PositiveSmallIntegerField(
        'Día del mes',
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fixed_incomes',
        verbose_name='Cuenta bancaria'
    )
    is_active = models.BooleanField('Activo', default=True)
    last_processed_date = models.DateField(
        'Última fecha procesada',
        null=True,
        blank=True,
        help_text='Fecha del último mes en que se convirtió a ingreso real'
    )
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Ingreso fijo'
        verbose_name_plural = 'Ingresos fijos'
        ordering = ['day_of_month', 'name']

    def __str__(self):
        symbol = 'S/' if self.currency == 'PEN' else '$'
        return f"{self.name} - {symbol} {self.amount}"


class CreditCardPayment(models.Model):
    """Modelo para pagos de tarjetas de crédito."""

    CURRENCY_CHOICES = [
        ('PEN', 'Soles'),
        ('USD', 'Dólares'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_card_payments',
        verbose_name='Usuario'
    )
    credit_card = models.ForeignKey(
        CreditCard,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Tarjeta de crédito'
    )
    amount = models.DecimalField(
        'Monto del pago',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    currency = models.CharField(
        'Moneda del pago',
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='PEN',
        help_text='Moneda en la que se realiza el pago'
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credit_card_payments',
        verbose_name='Cuenta bancaria'
    )
    date = models.DateField('Fecha del pago')
    description = models.CharField(
        'Descripción',
        max_length=255,
        blank=True,
        default=''
    )
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'Pago de tarjeta'
        verbose_name_plural = 'Pagos de tarjetas'
        ordering = ['-date', '-created_at']

    def __str__(self):
        symbol = 'S/' if self.currency == 'PEN' else '$'
        return f"Pago {self.credit_card.name} - {symbol} {self.amount}"

    def save(self, *args, **kwargs):
        """Al guardar, reduce el saldo usado de la tarjeta."""
        is_new = self._state.adding
        old_instance = None

        if not is_new:
            old_instance = CreditCardPayment.objects.filter(pk=self.pk).first()

        super().save(*args, **kwargs)

        # Si es edición, revertir el pago anterior
        if old_instance:
            self._revert_payment(old_instance)

        # Aplicar el nuevo pago
        self._apply_payment()

    def delete(self, *args, **kwargs):
        """Al eliminar, revierte el pago (suma al saldo usado)."""
        card = self.credit_card
        amount = self.amount
        currency = self.currency
        super().delete(*args, **kwargs)

        # Revertir: sumar de vuelta al usado
        if currency == 'PEN':
            card.used_pen += amount
        else:
            card.used_usd += amount
        card.save(update_fields=['used_pen', 'used_usd', 'updated_at'])

    def _apply_payment(self):
        """Reduce el saldo usado de la tarjeta según la moneda del pago."""
        card = self.credit_card
        if self.currency == 'PEN':
            card.used_pen = max(0, card.used_pen - self.amount)
        else:
            card.used_usd = max(0, card.used_usd - self.amount)
        card.save(update_fields=['used_pen', 'used_usd', 'updated_at'])

    def _revert_payment(self, old_instance):
        """Revierte un pago anterior (para ediciones)."""
        card = old_instance.credit_card
        if old_instance.currency == 'PEN':
            card.used_pen += old_instance.amount
        else:
            card.used_usd += old_instance.amount
        card.save(update_fields=['used_pen', 'used_usd', 'updated_at'])
