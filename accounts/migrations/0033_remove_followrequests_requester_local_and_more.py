# Generated by Django 4.2.6 on 2023-11-21 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0032_alter_followrequests_unique_together_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='followrequests',
            name='requester_local',
        ),
        migrations.AddField(
            model_name='followrequests',
            name='requester_host',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
