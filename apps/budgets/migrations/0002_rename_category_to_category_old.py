# Generated manually for category migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
        ('budgets', '0001_initial'),
    ]

    operations = [
        # Paso 1: Quitar unique_together antes de renombrar el campo
        migrations.AlterUniqueTogether(
            name='budget',
            unique_together=set(),
        ),

        # Paso 2: Renombrar category a category_old
        migrations.RenameField(
            model_name='budget',
            old_name='category',
            new_name='category_old',
        ),

        # Paso 3: Agregar nuevo campo category como ForeignKey
        migrations.AddField(
            model_name='budget',
            name='category',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='budgets',
                to='categories.category',
                verbose_name='Categoría'
            ),
        ),
    ]
