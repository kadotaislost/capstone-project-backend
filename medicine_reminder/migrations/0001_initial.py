# Generated by Django 5.1 on 2024-09-29 09:02

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medication_name', models.CharField(max_length=100)),
                ('reason_for_medication', models.CharField(max_length=200)),
                ('frequency', models.CharField(choices=[('daily', 'Everyday'), ('every_x_days', 'Every X days'), ('day_of_week', 'Day of the week'), ('day_of_month', 'Day of the month')], max_length=20)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('memo', models.TextField(blank=True)),
                ('repeat', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('day_of_week', models.JSONField(blank=True, null=True)),
                ('day_of_month', models.JSONField(blank=True, null=True)),
                ('every_x_days', models.PositiveIntegerField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReminderTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField()),
                ('dosage', models.CharField(max_length=50)),
                ('reminder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='times', to='medicine_reminder.reminder')),
            ],
        ),
    ]