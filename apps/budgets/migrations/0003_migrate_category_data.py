# Generated manually for category data migration

from django.db import migrations


# Mapeo de categorías legacy a nombres
CATEGORY_MAPPING = {
    'food': {'name': 'Comida', 'icon': '🍔', 'color': '#f97316'},
    'transport': {'name': 'Transporte', 'icon': '🚗', 'color': '#3b82f6'},
    'entertainment': {'name': 'Entretenimiento', 'icon': '🎬', 'color': '#8b5cf6'},
    'shopping': {'name': 'Compras', 'icon': '🛒', 'color': '#ec4899'},
    'bills': {'name': 'Servicios', 'icon': '📄', 'color': '#6b7280'},
    'health': {'name': 'Salud', 'icon': '🏥', 'color': '#10b981'},
    'other': {'name': 'Otros', 'icon': '📦', 'color': '#64748b'},
}


def migrate_categories_forward(apps, schema_editor):
    """Migra los datos de category_old a category (FK)."""
    Category = apps.get_model('categories', 'Category')
    Budget = apps.get_model('budgets', 'Budget')

    # Cache de categorías por usuario
    user_categories = {}

    def get_or_create_category(user, legacy_key):
        """Obtiene o crea una categoría para el usuario."""
        if user.id not in user_categories:
            user_categories[user.id] = {}

        if legacy_key not in user_categories[user.id]:
            mapping = CATEGORY_MAPPING.get(legacy_key, CATEGORY_MAPPING['other'])
            category, _ = Category.objects.get_or_create(
                user=user,
                name=mapping['name'],
                type='expense',
                defaults={
                    'icon': mapping['icon'],
                    'color': mapping['color'],
                }
            )
            user_categories[user.id][legacy_key] = category

        return user_categories[user.id][legacy_key]

    # Migrar Budgets
    for budget in Budget.objects.select_related('user').all():
        if budget.category_old:
            budget.category = get_or_create_category(budget.user, budget.category_old)
            budget.save(update_fields=['category'])


def migrate_categories_backward(apps, schema_editor):
    """Revierte la migración."""
    Budget = apps.get_model('budgets', 'Budget')

    NAME_TO_KEY = {v['name']: k for k, v in CATEGORY_MAPPING.items()}

    for budget in Budget.objects.select_related('category').all():
        if budget.category:
            budget.category_old = NAME_TO_KEY.get(budget.category.name, 'other')
            budget.save(update_fields=['category_old'])


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0002_rename_category_to_category_old'),
    ]

    operations = [
        migrations.RunPython(migrate_categories_forward, migrate_categories_backward),
    ]
