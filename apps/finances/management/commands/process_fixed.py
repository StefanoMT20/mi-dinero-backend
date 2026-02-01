"""
Comando para procesar ingresos/gastos fijos pendientes.

Uso:
    python manage.py process_fixed
    python manage.py process_fixed --user=username
    python manage.py process_fixed --all-users
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.finances.models import FixedExpense, FixedIncome, Expense, Income

User = get_user_model()


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

    def handle(self, *args, **options):
        today = timezone.now().date()
        current_month_start = today.replace(day=1)

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

        for user in users:
            self.stdout.write(f"\nProcesando usuario: {user.username}")

            # Procesar gastos fijos
            pending_expenses = FixedExpense.objects.filter(
                user=user,
                is_active=True,
                day_of_month__lte=today.day
            ).exclude(
                last_processed_date__gte=current_month_start
            )

            for fixed in pending_expenses:
                expense_date = today.replace(day=min(fixed.day_of_month, today.day))
                Expense.objects.create(
                    user=user,
                    amount=fixed.amount,
                    currency=fixed.currency,
                    category=fixed.category,
                    description=f"{fixed.name} (Fijo)",
                    date=expense_date,
                    credit_card=fixed.credit_card,
                    bank_account=fixed.bank_account,
                )
                fixed.last_processed_date = today
                fixed.save(update_fields=['last_processed_date'])
                total_expenses += 1
                self.stdout.write(f"  ✓ Gasto fijo: {fixed.name} - {fixed.currency} {fixed.amount}")

            # Procesar ingresos fijos
            pending_incomes = FixedIncome.objects.filter(
                user=user,
                is_active=True,
                day_of_month__lte=today.day
            ).exclude(
                last_processed_date__gte=current_month_start
            )

            for fixed in pending_incomes:
                income_date = today.replace(day=min(fixed.day_of_month, today.day))
                Income.objects.create(
                    user=user,
                    amount=fixed.amount,
                    currency=fixed.currency,
                    category=fixed.category,
                    description=f"{fixed.name} (Fijo)",
                    date=income_date,
                    bank_account=fixed.bank_account,
                )
                fixed.last_processed_date = today
                fixed.save(update_fields=['last_processed_date'])
                total_incomes += 1
                self.stdout.write(f"  ✓ Ingreso fijo: {fixed.name} - {fixed.currency} {fixed.amount}")

        self.stdout.write(self.style.SUCCESS(
            f"\n¡Listo! Procesados: {total_expenses} gastos y {total_incomes} ingresos"
        ))
