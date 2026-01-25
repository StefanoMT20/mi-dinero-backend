# Generated manually for removing legacy category field

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0003_migrate_category_data'),
        ('categories', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Eliminar campo category_old
        migrations.RemoveField(
            model_name='budget',
            name='category_old',
        ),

        # Actualizar el campo category para que no sea nullable
        migrations.AlterField(
            model_name='budget',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='budgets',
                to='categories.category',
                verbose_name='Categoría'
            ),
        ),

        # Restaurar unique_together con el nuevo campo FK
        migrations.AlterUniqueTogether(
            name='budget',
            unique_together={('user', 'category')},
        ),
    ]
