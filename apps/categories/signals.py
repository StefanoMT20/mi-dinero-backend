from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


# Categorías por defecto para gastos
DEFAULT_EXPENSE_CATEGORIES = [
    {'name': 'Alimentación', 'icon': '🍔', 'color': '#f97316'},
    {'name': 'Transporte', 'icon': '🚗', 'color': '#3b82f6'},
    {'name': 'Entretenimiento', 'icon': '🎬', 'color': '#8b5cf6'},
    {'name': 'Salud', 'icon': '💊', 'color': '#ef4444'},
    {'name': 'Educación', 'icon': '📚', 'color': '#06b6d4'},
    {'name': 'Ropa', 'icon': '👕', 'color': '#ec4899'},
    {'name': 'Hogar', 'icon': '🏠', 'color': '#84cc16'},
    {'name': 'Servicios', 'icon': '💡', 'color': '#f59e0b'},
    {'name': 'Suscripciones', 'icon': '📱', 'color': '#6366f1'},
    {'name': 'Restaurantes', 'icon': '🍽️', 'color': '#14b8a6'},
    {'name': 'Supermercado', 'icon': '🛒', 'color': '#22c55e'},
    {'name': 'Mascotas', 'icon': '🐕', 'color': '#a855f7'},
    {'name': 'Regalos', 'icon': '🎁', 'color': '#f43f5e'},
    {'name': 'Viajes', 'icon': '✈️', 'color': '#0ea5e9'},
    {'name': 'Otros gastos', 'icon': '📦', 'color': '#64748b'},
]

# Categorías por defecto para ingresos
DEFAULT_INCOME_CATEGORIES = [
    {'name': 'Salario', 'icon': '💰', 'color': '#22c55e'},
    {'name': 'Freelance', 'icon': '💻', 'color': '#3b82f6'},
    {'name': 'Inversiones', 'icon': '📈', 'color': '#8b5cf6'},
    {'name': 'Alquiler', 'icon': '🏢', 'color': '#f97316'},
    {'name': 'Ventas', 'icon': '🛍️', 'color': '#ec4899'},
    {'name': 'Bonos', 'icon': '🎯', 'color': '#14b8a6'},
    {'name': 'Comisiones', 'icon': '💵', 'color': '#f59e0b'},
    {'name': 'Regalos', 'icon': '🎁', 'color': '#f43f5e'},
    {'name': 'Reembolsos', 'icon': '↩️', 'color': '#06b6d4'},
    {'name': 'Otros ingresos', 'icon': '📥', 'color': '#64748b'},
]


def create_default_categories_for_user(user):
    """Crea las categorías por defecto para un usuario."""
    from .models import Category

    categories_to_create = []

    # Crear categorías de gastos
    for cat_data in DEFAULT_EXPENSE_CATEGORIES:
        if not Category.objects.filter(user=user, name=cat_data['name'], type='expense').exists():
            categories_to_create.append(
                Category(
                    user=user,
                    name=cat_data['name'],
                    icon=cat_data['icon'],
                    color=cat_data['color'],
                    type='expense'
                )
            )

    # Crear categorías de ingresos
    for cat_data in DEFAULT_INCOME_CATEGORIES:
        if not Category.objects.filter(user=user, name=cat_data['name'], type='income').exists():
            categories_to_create.append(
                Category(
                    user=user,
                    name=cat_data['name'],
                    icon=cat_data['icon'],
                    color=cat_data['color'],
                    type='income'
                )
            )

    if categories_to_create:
        Category.objects.bulk_create(categories_to_create)

    return len(categories_to_create)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_default_categories(sender, instance, created, **kwargs):
    """Señal que crea categorías por defecto cuando se registra un nuevo usuario."""
    if created:
        create_default_categories_for_user(instance)
