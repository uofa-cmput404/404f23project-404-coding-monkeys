from django.db import migrations, models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_authoruser_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authoruser',
            name='uuid',
            field=models.CharField(max_length=36, unique=True),
        ),
    ]
