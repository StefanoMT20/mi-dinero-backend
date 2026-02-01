"""
Comando para procesar ingresos/gastos fijos pendientes.

Uso:
    python manage.py process_fixed --all-users
    python manage.py process_fixed --user=username
    python manage.py process_fixed --all-users --backfill  # Procesa meses anteriores pendientes
"""
import calendar
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.finances.models import FixedExpense, FixedIncome, Expense, Income

User = get_user_model()


def add_months(source_date, months):
    """Suma o resta meses a una fecha."""
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def last_day_of_month(d):
    """Retorna el último día del mes."""
    return calendar.monthrange(d.year, d.month)[1]


class Command(BaseCommand):
    help = 'Procesa ingresos y gastos fijos pendientes, convirtiéndolos en reales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username del usuario a procesar',
        )
        parser.add_argument(
            '--all-users',
            action='store_true',
            help='Procesar para todos los usuarios',
        )
        parser.add_argument(
            '--backfill',
            action='store_true',
            help='Procesar también meses anteriores pendientes (hasta 12 meses atrás)',
        )
        parser.add_argument(
            '--months-back',
            type=int,
            default=12,
            help='Cuántos meses atrás revisar con --backfill (default: 12)',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()

        if options['user']:
            try:
                users = [User.objects.get(username=options['user'])]
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Usuario '{options['user']}' no encontrado"))
                return
        elif options['all_users']:
            users = User.objects.all()
        else:
            self.stderr.write(self.style.ERROR(
                "Debes especificar --user=username o --all-users"
            ))
            return

        total_expenses = 0
        total_incomes = 0
        backfill = options['backfill']
        months_back = options['months_back']

        for user in users:
            self.stdout.write(f"\nProcesando usuario: {user.username}")

            # Procesar gastos fijos
            fixed_expenses = FixedExpense.objects.filter(user=user, is_active=True)
            for fixed in fixed_expenses:
                processed = self._process_fixed_expense(fixed, today, backfill, months_back)
                total_expenses += processed

            # Procesar ingresos fijos
            fixed_incomes = FixedIncome.objects.filter(user=user, is_active=True)
            for fixed in fixed_incomes:
                processed = self._process_fixed_income(fixed, today, backfill, months_back)
                total_incomes += processed

        self.stdout.write(self.style.SUCCESS(
            f"\n¡Listo! Procesados: {total_expenses} gastos y {total_incomes} ingresos"
        ))

    def _get_months_to_process(self, fixed, today, backfill, months_back):
        """Determina qué meses necesitan ser procesados."""
        months = []
        current_month = today.replace(day=1)

        if backfill:
            # Revisar meses anteriores
            start_month = add_months(current_month, -months_back)
            # No procesar antes de la fecha de creación del ingreso/gasto fijo
            created_month = fixed.created_at.date().replace(day=1)
            if start_month < created_month:
                start_month = created_month
        else:
            start_month = current_month

        # Iterar desde start_month hasta current_month
        check_month = start_month
        while check_month <= current_month:
            # Determinar la fecha del ingreso/gasto en este mes
            day = min(fixed.day_of_month, last_day_of_month(check_month))
            target_date = check_month.replace(day=day)

            # Solo procesar si la fecha ya pasó (o es hoy)
            if target_date <= today:
                # Verificar si ya fue procesado este mes
                month_start = check_month
                next_month = add_months(check_month, 1)

                already_processed = False
                if fixed.last_processed_date:
                    # Si last_processed_date está dentro de este mes, ya fue procesado
                    if month_start <= fixed.last_processed_date < next_month:
                        already_processed = True
                    # Si last_processed_date es posterior a este mes, también ya pasó
                    elif fixed.last_processed_date >= next_month:
                        already_processed = True

                if not already_processed:
                    months.append(target_date)

            check_month = add_months(check_month, 1)

        return months

    def _process_fixed_expense(self, fixed, today, backfill, months_back):
        """Procesa un gasto fijo para los meses pendientes."""
        months = self._get_months_to_process(fixed, today, backfill, months_back)
        count = 0

        for target_date in months:
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
            count += 1
            self.stdout.write(f"  ✓ Gasto fijo: {fixed.name} - {fixed.currency} {fixed.amount} ({target_date})")

        if count > 0:
            fixed.last_processed_date = today
            fixed.save(update_fields=['last_processed_date'])

        return count

    def _process_fixed_income(self, fixed, today, backfill, months_back):
        """Procesa un ingreso fijo para los meses pendientes."""
        months = self._get_months_to_process(fixed, today, backfill, months_back)
        count = 0

        for target_date in months:
            Income.objects.create(
                user=fixed.user,
                amount=fixed.amount,
                currency=fixed.currency,
                category=fixed.category,
                description=f"{fixed.name} (Fijo)",
                date=target_date,
                bank_account=fixed.bank_account,
            )
            count += 1
            self.stdout.write(f"  ✓ Ingreso fijo: {fixed.name} - {fixed.currency} {fixed.amount} ({target_date})")

        if count > 0:
            fixed.last_processed_date = today
            fixed.save(update_fields=['last_processed_date'])

        return count
