# Generated manually for removing legacy category fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0008_migrate_category_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expense',
            name='category_old',
        ),
        migrations.RemoveField(
            model_name='fixedexpense',
            name='category_old',
        ),
        migrations.RemoveField(
            model_name='income',
            name='category_old',
        ),
    ]
