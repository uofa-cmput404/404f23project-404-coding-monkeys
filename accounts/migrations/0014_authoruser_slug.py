# Generated by Django 4.2.6 on 2023-11-08 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_alter_authoruser_host'),
    ]

    operations = [
        migrations.AddField(
            model_name='authoruser',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]
