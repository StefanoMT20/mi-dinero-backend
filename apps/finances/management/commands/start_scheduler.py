"""
Scheduler de tareas automáticas usando APScheduler.
Corre como proceso independiente dentro del mismo contenedor.

Uso:
    python manage.py start_scheduler
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


def process_fixed_transactions():
    """Procesa todos los gastos e ingresos fijos pendientes para todos los usuarios."""
    from apps.finances.models import FixedExpense, FixedIncome, Expense, Income

    today = date.today()
    current_month_start = today.replace(day=1)
    total_expenses = 0
    total_incomes = 0

    for fixed in FixedExpense.objects.filter(is_active=True).select_related('user', 'category', 'credit_card', 'bank_account'):
        if fixed.last_processed_date and fixed.last_processed_date >= current_month_start:
            continue
        day = min(fixed.day_of_month, last_day_of_month(current_month_start))
        target_date = current_month_start.replace(day=day)
        if target_date > today:
            continue
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
        fixed.last_processed_date = today
        fixed.save(update_fields=['last_processed_date'])
        total_expenses += 1

    for fixed in FixedIncome.objects.filter(is_active=True).select_related('user', 'category', 'bank_account'):
        if fixed.last_processed_date and fixed.last_processed_date >= current_month_start:
            continue
        day = min(fixed.day_of_month, last_day_of_month(current_month_start))
        target_date = current_month_start.replace(day=day)
        if target_date > today:
            continue
        Income.objects.create(
            user=fixed.user,
            amount=fixed.amount,
            currency=fixed.currency,
            category=fixed.category,
            description=f"{fixed.name} (Fijo)",
            date=target_date,
            bank_account=fixed.bank_account,
        )
        fixed.last_processed_date = today
        fixed.save(update_fields=['last_processed_date'])
        total_incomes += 1

    logger.info(f"Procesados: {total_expenses} gastos y {total_incomes} ingresos")


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

        self.stdout.write(self.style.SUCCESS('Scheduler iniciado. Corre los días 1 y 16 de cada mes a las 6am.'))
        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
