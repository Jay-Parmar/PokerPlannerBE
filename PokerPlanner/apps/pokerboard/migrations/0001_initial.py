# Generated by Django 2.2 on 2021-10-25 09:39

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(blank=True, help_text='Non existing user email', max_length=254, null=True)),
                ('is_accepted', models.BooleanField(default=False, help_text='Indicates if invitation accepted or not')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ManagerCredentials',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('username', models.EmailField(help_text='Jira Username', max_length=254)),
                ('password', models.CharField(help_text='Jira Password or Token', max_length=250)),
                ('url', models.URLField(help_text="User's Jira Url")),
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
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('estimate_type', models.PositiveSmallIntegerField(choices=[(1, 'Series'), (2, 'Even'), (3, 'Odd'), (4, 'Fibonacci'), (5, 'Custom')], default=1, help_text='Estimation type')),
                ('title', models.CharField(help_text='Name of Pokerboard', max_length=20, unique=True)),
                ('description', models.CharField(blank=True, help_text='Description', max_length=100, null=True)),
                ('timer', models.PositiveIntegerField(help_text='Duration for voting (in seconds)', null=True)),
                ('estimation_cards', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), help_text='Array of estimation values choosed by user', null=True, size=None)),
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
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
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
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
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
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('estimate', models.PositiveIntegerField(help_text='Final estimate of ticket')),
                ('estimation_time', models.PositiveIntegerField(help_text='Time taken by user to estimate (in seconds)')),
                ('ticket_id', models.ForeignKey(help_text='Ticket ID on database', on_delete=django.db.models.deletion.CASCADE, related_name='estimations', to='pokerboard.Ticket')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
