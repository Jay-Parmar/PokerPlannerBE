# Generated by Django 2.2 on 2021-10-06 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0002_auto_20211005_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='isDeleted',
        ),
        migrations.AddField(
            model_name='group',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
