# Generated by Django 4.2.6 on 2023-11-23 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0018_remove_likes_visibility'),
    ]

    operations = [
        migrations.AddField(
            model_name='likes',
            name='liked_id',
            field=models.CharField(default='temp', max_length=36),
            preserve_default=False,
        ),
    ]
