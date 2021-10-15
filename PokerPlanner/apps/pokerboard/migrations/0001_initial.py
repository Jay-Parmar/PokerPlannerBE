# Generated by Django 2.2 on 2021-10-05 16:00

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('isDeleted', models.BooleanField(default=False)),
                ('email', models.EmailField(help_text='Non existing user email', max_length=254, null=True)),
                ('is_accepted', models.BooleanField(default=False, help_text='Indicates if invitation accepted or not')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pokerboard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('isDeleted', models.BooleanField(default=False)),
                ('estimate_type', models.PositiveSmallIntegerField(choices=[(1, 'Series'), (2, 'Even'), (3, 'Odd'), (4, 'Fibonacci')], default=1, help_text='Estimation type')),
                ('title', models.CharField(help_text='Name of Pokerboard', max_length=20, unique=True)),
                ('description', models.CharField(help_text='Description', max_length=100, null=True)),
                ('timer', models.PositiveIntegerField(help_text='Duration for voting (in seconds)')),
                ('estimation_cards', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), help_text='Array of estimation values choosed by user', size=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PokerboardGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('isDeleted', models.BooleanField(default=False)),
                ('role', models.PositiveSmallIntegerField(choices=[(1, 'Spectator'), (2, 'Contributor')], default=2, help_text='Role')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PokerboardUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('isDeleted', models.BooleanField(default=False)),
                ('role', models.PositiveSmallIntegerField(choices=[(1, 'Spectator'), (2, 'Contributor')], default=2, help_text='Role')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('isDeleted', models.BooleanField(default=False)),
                ('ticket_id', models.SlugField(help_text='Ticket ID imported from JIRA')),
                ('estimate', models.PositiveIntegerField(help_text='Final estimate of ticket', null=True)),
                ('order', models.PositiveIntegerField(help_text='Order of displaying of tickets')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Untouched'), (2, 'Ongoing'), (3, 'Estimated'), (4, 'Skipped')], default=1, help_text='Status of ticket')),
                ('start_datetime', models.DateTimeField(null=True)),
                ('end_datetime', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserTicketEstimate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estimate', models.PositiveIntegerField(help_text='Final estimate of ticket')),
                ('estimation_time', models.PositiveIntegerField(help_text='Time taken by user to estimate (in seconds)')),
                ('ticket_id', models.ForeignKey(help_text='Ticket ID on database', on_delete=django.db.models.deletion.DO_NOTHING, related_name='estimations', to='pokerboard.Ticket')),
            ],
        ),
    ]