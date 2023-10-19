# Generated by Django 4.2.6 on 2023-10-19 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_followrequests_followers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authoruser',
            name='github',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='authoruser',
            name='profile_image',
            field=models.URLField(blank=True, null=True),
        ),
    ]
