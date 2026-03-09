"""
Scheduler de tareas automáticas usando APScheduler.
Corre como proceso independiente dentro del mismo contenedor.

Uso:
    python manage.py start_scheduler

Lógica del job (corre días 1 y 16 de cada mes):
- Revisa el mes actual Y el mes anterior para no perder gastos del 17-31.
- Un gasto fijo con day_of_month=25 no se procesa hasta que el día 25 haya llegado.
- Solo se procesa UNA vez por mes (tracking via last_processed_date = target_date).
"""
import calendar
import logging
from datetime import date
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def last_day_of_month(d):
    return calendar.monthrange(d.year, d.month)[1]


def _already_processed_in_month(last_processed_date, month_start):
    """Verifica si el gasto ya fue procesado para el mes dado."""
    if not last_processed_date:
        return False
    next_month = add_months(month_start, 1)
    return month_start <= last_processed_date < next_month


def _get_pending_months(fixed, today):
    """
    Retorna las fechas target pendientes de procesar.
    Revisa el mes anterior y el mes actual para cubrir todos los day_of_month (1-31).
    """
    current_month_start = today.replace(day=1)
    prev_month_start = add_months(current_month_start, -1)
    pending = []

    for month_start in [prev_month_start, current_month_start]:
        day = min(fixed.day_of_month, last_day_of_month(month_start))
        target_date = month_start.replace(day=day)

        # Requisito 2 y 3: solo si la fecha ya llegó o pasó
        if target_date > today:
            continue

        # Requisito 4: solo una vez por mes
        if _already_processed_in_month(fixed.last_processed_date, month_start):
            continue

        pending.append(target_date)

    return pending


def process_fixed_transactions():
    """Procesa todos los gastos e ingresos fijos pendientes para todos los usuarios."""
    from apps.finances.models import FixedExpense, FixedIncome, Expense, Income

    today = date.today()
    total_expenses = 0
    total_incomes = 0

    for fixed in FixedExpense.objects.filter(is_active=True).select_related(
        'user', 'category', 'credit_card', 'bank_account'
    ):
        for target_date in _get_pending_months(fixed, today):
            Expense.objects.create(
                user=fixed.user,
                amount=fixed.amount,
                currency=fixed.currency,
                category=fixed.category,
                description=f"{fixed.name} (Fijo)",
                date=target_date,
                credit_card=fixed.credit_card,
                bank_account=fixed.bank_account,
            )
            # Guardamos target_date (no today) para el tracking correcto por mes
            fixed.last_processed_date = target_date
            fixed.save(update_fields=['last_processed_date'])
            total_expenses += 1
            logger.info(f"Gasto fijo procesado: {fixed.name} - {target_date}")

    for fixed in FixedIncome.objects.filter(is_active=True).select_related(
        'user', 'category', 'bank_account'
    ):
        for target_date in _get_pending_months(fixed, today):
            Income.objects.create(
                user=fixed.user,
                amount=fixed.amount,
                currency=fixed.currency,
                category=fixed.category,
                description=f"{fixed.name} (Fijo)",
                date=target_date,
                bank_account=fixed.bank_account,
            )
            fixed.last_processed_date = target_date
            fixed.save(update_fields=['last_processed_date'])
            total_incomes += 1
            logger.info(f"Ingreso fijo procesado: {fixed.name} - {target_date}")

    logger.info(f"Job completado: {total_expenses} gastos y {total_incomes} ingresos procesados")


class Command(BaseCommand):
    help = 'Inicia el scheduler de tareas automáticas'

    def handle(self, *args, **options):
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger
        from django_apscheduler.jobstores import DjangoJobStore

        scheduler = BlockingScheduler(timezone='America/Lima')
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        scheduler.add_job(
            process_fixed_transactions,
            trigger=CronTrigger(day='1,16', hour=6, minute=0),
            id='process_fixed_transactions',
            name='Procesar gastos e ingresos fijos',
            jobstore='default',
            replace_existing=True,
        )

        self.stdout.write(self.style.SUCCESS(
            'Scheduler iniciado. Corre los días 1 y 16 de cada mes a las 6am (Lima).'
        ))
        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
