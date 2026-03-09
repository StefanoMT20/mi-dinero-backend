"""
Script para debuggear el problema de balance.
Ejecutar con: python manage.py shell < check_balance.py
"""

from apps.finances.models import BankAccount, Income
from django.contrib.auth import get_user_model

User = get_user_model()

# Cambia esto por tu username
USERNAME = "tu_username_aqui"

user = User.objects.get(username=USERNAME)

print("\n=== CUENTAS BANCARIAS ===")
for account in BankAccount.objects.filter(user=user):
    print(f"\nCuenta: {account.name}")
    print(f"  Moneda: {account.currency}")
    print(f"  Balance inicial: {account.balance}")
    print(f"  Balance calculado: {account.calculated_balance}")
    print(f"  balance_updated_at: {account.balance_updated_at}")
    print(f"  add_incomes: {account.add_incomes}")
    print(f"  subtract_expenses: {account.subtract_expenses}")
    print(f"  Total ingresos contados: {account.total_income}")
    print(f"  Total gastos contados: {account.total_expenses}")

    print(f"\n  Ingresos de esta cuenta ({account.currency}):")
    incomes = account.incomes.filter(currency=account.currency).order_by('-created_at')
    for income in incomes[:5]:  # Últimos 5
        print(f"    - {income.description}: {income.amount} {income.currency}")
        print(f"      created_at: {income.created_at}")
        if account.balance_updated_at:
            incluido = income.created_at >= account.balance_updated_at
            print(f"      ¿Incluido en balance?: {'SÍ' if incluido else 'NO'}")
