import uuid
from django.conf import settings
from django.db import models


class GoalCategory(models.TextChoices):
    CAREER = 'career', 'Carrera'
    HEALTH = 'health', 'Salud'
    EDUCATION = 'education', 'Educación'
    FINANCE = 'finance', 'Finanzas'
    PERSONAL = 'personal', 'Personal'
    RELATIONSHIPS = 'relationships', 'Relaciones'


class GoalStatus(models.TextChoices):
    NOT_STARTED = 'not_started', 'Sin iniciar'
    IN_PROGRESS = 'in_progress', 'En progreso'
    COMPLETED = 'completed', 'Completado'
    PAUSED = 'paused', 'Pausado'


class FinanceGoalType(models.TextChoices):
    SAVINGS = 'savings', 'Ahorro'
    EXPENSE_LIMIT = 'expense_limit', 'Límite de gasto'


class MeasurementType(models.TextChoices):
    NUMERIC = 'numeric', 'Numérico'
    CURRENCY = 'currency', 'Monetario'
    PERCENTAGE = 'percentage', 'Porcentaje'
    BOOLEAN = 'boolean', 'Sí/No'
    MILESTONE = 'milestone', 'Hitos'


class Objective(models.Model):
    """Modelo para objetivos (la O de OKR)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='objectives',
        verbose_name='Usuario'
    )
    title = models.CharField('Título', max_length=200)
    description = models.TextField('Descripción', blank=True)
    category = models.CharField(
        'Categoría',
        max_length=20,
        choices=GoalCategory.choices
    )
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=GoalStatus.choices,
        default=GoalStatus.NOT_STARTED
    )
    start_date = models.DateField('Fecha de inicio')
    end_date = models.DateField('Fecha de fin')

    # Vinculación opcional con finanzas
    linked_finance_type = models.CharField(
        'Tipo de meta financiera',
        max_length=20,
        choices=FinanceGoalType.choices,
        null=True,
        blank=True
    )
    linked_finance_target = models.DecimalField(
        'Meta financiera',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Objetivo'
        verbose_name_plural = 'Objetivos'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def progress(self):
        """Calcula el progreso basado en los key results."""
        if self.status == GoalStatus.COMPLETED:
            return 100

        key_results = self.key_results.all()
        if not key_results:
            return 0

        total = sum(kr.progress for kr in key_results)
        return round(total / len(key_results))


class KeyResult(models.Model):
    """Modelo para resultados clave (la KR de OKR)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    objective = models.ForeignKey(
        Objective,
        on_delete=models.CASCADE,
        related_name='key_results',
        verbose_name='Objetivo'
    )
    title = models.CharField('Título', max_length=200)
    measurement_type = models.CharField(
        'Tipo de medición',
        max_length=20,
        choices=MeasurementType.choices,
        default=MeasurementType.NUMERIC
    )
    current_value = models.DecimalField(
        'Valor actual',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    target_value = models.DecimalField(
        'Valor objetivo',
        max_digits=12,
        decimal_places=2
    )
    unit = models.CharField('Unidad', max_length=50, blank=True, default='')
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = 'Resultado Clave'
        verbose_name_plural = 'Resultados Clave'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.title} ({self.current_value}/{self.target_value} {self.unit})"

    @property
    def progress(self):
        """Calcula el porcentaje de progreso."""
        if self.target_value <= 0:
            return 0
        return min(round((self.current_value / self.target_value) * 100), 100)


class Milestone(models.Model):
    """Modelo para hitos de un KeyResult."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key_result = models.ForeignKey(
        KeyResult,
        on_delete=models.CASCADE,
        related_name='milestones',
        verbose_name='Resultado Clave'
    )
    title = models.CharField('Título', max_length=255)
    completed = models.BooleanField('Completado', default=False)
    order = models.PositiveIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Hito'
        verbose_name_plural = 'Hitos'
        ordering = ['order']

    def __str__(self):
        status = '✓' if self.completed else '○'
        return f"{status} {self.title}"
