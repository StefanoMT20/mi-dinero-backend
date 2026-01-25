# Generated manually for removing legacy category field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0003_migrate_category_data'),
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
    ]
