# Generated by Django 3.2.7 on 2021-10-09 04:13

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokerboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokerboard',
            name='estimation_cards',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), help_text='Array of estimation values choosed by user', null=True, size=None),
        ),
        migrations.AlterField(
            model_name='pokerboard',
            name='timer',
            field=models.PositiveIntegerField(help_text='Duration for voting (in seconds)', null=True),
        ),
    ]