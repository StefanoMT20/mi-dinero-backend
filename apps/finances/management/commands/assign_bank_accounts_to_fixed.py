from django.core.management.base import BaseCommand
from apps.finances.models import BankAccount, FixedExpense, FixedIncome


class Command(BaseCommand):
    help = 'Asigna cuentas bancarias a ingresos/gastos fijos que no tienen una asignada'

    def handle(self, *args, **options):
        fixed_incomes_updated = 0
        fixed_expenses_updated = 0

        # Procesar ingresos fijos sin cuenta bancaria
        fixed_incomes = FixedIncome.objects.filter(bank_account__isnull=True)
        for fi in fixed_incomes:
            bank_account = BankAccount.objects.filter(
                user=fi.user,
                currency=fi.currency
            ).first()
            if bank_account:
                fi.bank_account = bank_account
                fi.save(update_fields=['bank_account'])
                fixed_incomes_updated += 1
                self.stdout.write(
                    f'  Ingreso fijo "{fi.name}" ({fi.currency}) -> {bank_account.name}'
                )

        # Procesar gastos fijos sin cuenta bancaria
        fixed_expenses = FixedExpense.objects.filter(bank_account__isnull=True)
        for fe in fixed_expenses:
            bank_account = BankAccount.objects.filter(
                user=fe.user,
                currency=fe.currency
            ).first()
            if bank_account:
                fe.bank_account = bank_account
                fe.save(update_fields=['bank_account'])
                fixed_expenses_updated += 1
                self.stdout.write(
                    f'  Gasto fijo "{fe.name}" ({fe.currency}) -> {bank_account.name}'
                )

        self.stdout.write(self.style.SUCCESS(
            f'\nResultado: {fixed_incomes_updated} ingresos fijos y '
            f'{fixed_expenses_updated} gastos fijos actualizados'
        ))
