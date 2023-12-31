# Generated by Django 4.2.6 on 2023-11-21 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0031_alter_whitelistcontroller_whitelist_enabled'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='followrequests',
            unique_together={('requester_uuid', 'recipient_uuid')},
        ),
        migrations.AddField(
            model_name='followrequests',
            name='requester_local',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='followrequests',
            name='requester_url',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.RemoveField(
            model_name='followrequests',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='followrequests',
            name='requester',
        ),
    ]
