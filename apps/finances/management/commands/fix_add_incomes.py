"""
Comando para activar add_incomes en todas las cuentas existentes.

Uso:
    python manage.py fix_add_incomes
"""
from django.core.management.base import BaseCommand
from apps.finances.models import BankAccount


class Command(BaseCommand):
    help = 'Activa add_incomes=True en todas las cuentas bancarias existentes'

    def handle(self, *args, **options):
        updated = BankAccount.objects.filter(add_incomes=False).update(add_incomes=True)
        self.stdout.write(self.style.SUCCESS(
            f'Actualizadas {updated} cuentas bancarias con add_incomes=True'
        ))
