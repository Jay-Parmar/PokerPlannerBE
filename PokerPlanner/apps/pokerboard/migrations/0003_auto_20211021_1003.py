# Generated by Django 2.2 on 2021-10-21 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokerboard', '0002_auto_20211025_0939'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invite',
            name='is_accepted',
        ),
        migrations.AddField(
            model_name='invite',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Accepted'), (0, 'Pending'), (-1, 'Declined')], default=0, help_text='Indicates if invitation accepted or not'),
        ),
    ]
