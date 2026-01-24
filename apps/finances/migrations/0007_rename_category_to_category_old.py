# Generated manually for category migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
        ('finances', '0006_fixedexpense'),
    ]

    operations = [
        # Paso 1: Renombrar category a category_old en cada modelo
        migrations.RenameField(
            model_name='expense',
            old_name='category',
            new_name='category_old',
        ),
        migrations.RenameField(
            model_name='fixedexpense',
            old_name='category',
            new_name='category_old',
        ),
        migrations.RenameField(
            model_name='income',
            old_name='category',
            new_name='category_old',
        ),

        # Paso 2: Agregar nuevo campo category como ForeignKey
        migrations.AddField(
            model_name='expense',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='expenses',
                to='categories.category',
                verbose_name='Categoría'
            ),
        ),
        migrations.AddField(
            model_name='fixedexpense',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='fixed_expenses',
                to='categories.category',
                verbose_name='Categoría'
            ),
        ),
        migrations.AddField(
            model_name='income',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='incomes',
                to='categories.category',
                verbose_name='Categoría'
            ),
        ),
    ]
