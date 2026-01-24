# Generated manually for category data migration

from django.db import migrations


# Mapeo de categorías de gastos legacy a nombres/iconos/colores
EXPENSE_CATEGORY_MAPPING = {
    'food': {'name': 'Comida', 'icon': '🍔', 'color': '#f97316'},
    'transport': {'name': 'Transporte', 'icon': '🚗', 'color': '#3b82f6'},
    'entertainment': {'name': 'Entretenimiento', 'icon': '🎬', 'color': '#8b5cf6'},
    'shopping': {'name': 'Compras', 'icon': '🛒', 'color': '#ec4899'},
    'bills': {'name': 'Servicios', 'icon': '📄', 'color': '#6b7280'},
    'health': {'name': 'Salud', 'icon': '🏥', 'color': '#10b981'},
    'other': {'name': 'Otros', 'icon': '📦', 'color': '#64748b'},
}

# Mapeo de categorías de ingresos legacy a nombres/iconos/colores
INCOME_CATEGORY_MAPPING = {
    'salary': {'name': 'Sueldo', 'icon': '💰', 'color': '#22c55e'},
    'freelance': {'name': 'Freelance', 'icon': '💻', 'color': '#3b82f6'},
    'investment': {'name': 'Inversión', 'icon': '📈', 'color': '#8b5cf6'},
    'gift': {'name': 'Regalo', 'icon': '🎁', 'color': '#ec4899'},
    'refund': {'name': 'Reembolso', 'icon': '↩️', 'color': '#f97316'},
    'other': {'name': 'Otros', 'icon': '📦', 'color': '#64748b'},
}


def migrate_categories_forward(apps, schema_editor):
    """Migra los datos de category_old a category (FK)."""
    Category = apps.get_model('categories', 'Category')
    Expense = apps.get_model('finances', 'Expense')
    FixedExpense = apps.get_model('finances', 'FixedExpense')
    Income = apps.get_model('finances', 'Income')
    User = apps.get_model('users', 'User')

    # Cache de categorías creadas por usuario
    user_expense_categories = {}  # {user_id: {legacy_key: category}}
    user_income_categories = {}

    def get_or_create_expense_category(user, legacy_key):
        """Obtiene o crea una categoría de gasto para el usuario."""
        if user.id not in user_expense_categories:
            user_expense_categories[user.id] = {}

        if legacy_key not in user_expense_categories[user.id]:
            mapping = EXPENSE_CATEGORY_MAPPING.get(legacy_key, EXPENSE_CATEGORY_MAPPING['other'])
            category, _ = Category.objects.get_or_create(
                user=user,
                name=mapping['name'],
                type='expense',
                defaults={
                    'icon': mapping['icon'],
                    'color': mapping['color'],
                }
            )
            user_expense_categories[user.id][legacy_key] = category

        return user_expense_categories[user.id][legacy_key]

    def get_or_create_income_category(user, legacy_key):
        """Obtiene o crea una categoría de ingreso para el usuario."""
        if user.id not in user_income_categories:
            user_income_categories[user.id] = {}

        if legacy_key not in user_income_categories[user.id]:
            mapping = INCOME_CATEGORY_MAPPING.get(legacy_key, INCOME_CATEGORY_MAPPING['other'])
            category, _ = Category.objects.get_or_create(
                user=user,
                name=mapping['name'],
                type='income',
                defaults={
                    'icon': mapping['icon'],
                    'color': mapping['color'],
                }
            )
            user_income_categories[user.id][legacy_key] = category

        return user_income_categories[user.id][legacy_key]

    # Migrar Expenses
    for expense in Expense.objects.select_related('user').all():
        if expense.category_old:
            expense.category = get_or_create_expense_category(expense.user, expense.category_old)
            expense.save(update_fields=['category'])

    # Migrar FixedExpenses
    for fixed_expense in FixedExpense.objects.select_related('user').all():
        if fixed_expense.category_old:
            fixed_expense.category = get_or_create_expense_category(fixed_expense.user, fixed_expense.category_old)
            fixed_expense.save(update_fields=['category'])

    # Migrar Incomes
    for income in Income.objects.select_related('user').all():
        if income.category_old:
            income.category = get_or_create_income_category(income.user, income.category_old)
            income.save(update_fields=['category'])


def migrate_categories_backward(apps, schema_editor):
    """Revierte la migración (copia category.name de vuelta a category_old)."""
    Expense = apps.get_model('finances', 'Expense')
    FixedExpense = apps.get_model('finances', 'FixedExpense')
    Income = apps.get_model('finances', 'Income')

    # Mapeo inverso para expenses
    EXPENSE_NAME_TO_KEY = {v['name']: k for k, v in EXPENSE_CATEGORY_MAPPING.items()}
    INCOME_NAME_TO_KEY = {v['name']: k for k, v in INCOME_CATEGORY_MAPPING.items()}

    for expense in Expense.objects.select_related('category').all():
        if expense.category:
            expense.category_old = EXPENSE_NAME_TO_KEY.get(expense.category.name, 'other')
            expense.save(update_fields=['category_old'])

    for fixed_expense in FixedExpense.objects.select_related('category').all():
        if fixed_expense.category:
            fixed_expense.category_old = EXPENSE_NAME_TO_KEY.get(fixed_expense.category.name, 'other')
            fixed_expense.save(update_fields=['category_old'])

    for income in Income.objects.select_related('category').all():
        if income.category:
            income.category_old = INCOME_NAME_TO_KEY.get(income.category.name, 'other')
            income.save(update_fields=['category_old'])


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0007_rename_category_to_category_old'),
    ]

    operations = [
        migrations.RunPython(migrate_categories_forward, migrate_categories_backward),
    ]
