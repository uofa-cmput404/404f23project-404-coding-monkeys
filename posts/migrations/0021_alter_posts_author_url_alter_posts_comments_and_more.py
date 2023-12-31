# Generated by Django 4.2.6 on 2023-11-28 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0020_alter_posts_author_uuid_alter_posts_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='author_url',
            field=models.CharField(max_length=350, null=True),
        ),
        migrations.AlterField(
            model_name='posts',
            name='comments',
            field=models.URLField(max_length=350),
        ),
        migrations.AlterField(
            model_name='posts',
            name='origin',
            field=models.URLField(max_length=350),
        ),
        migrations.AlterField(
            model_name='posts',
            name='source',
            field=models.URLField(max_length=350),
        ),
        migrations.AlterField(
            model_name='posts',
            name='uuid',
            field=models.CharField(max_length=100, primary_key=True, serialize=False, unique=True),
        ),
    ]
