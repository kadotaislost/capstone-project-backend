from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


def get_default_date():
    return timezone.now().date()

class Reminder(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Everyday'),
        ('every_x_days', 'Every X days'),
        ('day_of_week', 'Day of the week'),
        ('day_of_month', 'Day of the month'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    medication_name = models.CharField(max_length=100, null=False, blank=False)
    reason_for_medication = models.CharField(max_length= 200,null=False, blank=False)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, blank=False, null=False)
    start_date = models.DateField(default=get_default_date)
    end_date = models.DateField(null=True, blank=True)
    memo = models.TextField(blank=True)
    repeat = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields based on frequency
    day_of_week = models.JSONField(blank=True, null=True)  # e.g., ["sun", "mon"]
    day_of_month = models.JSONField(blank=True, null=True)  # e.g., [3, 24, 31]
    every_x_days = models.PositiveIntegerField(blank=True, null=True)  # e.g., 5
    
    def clean(self):
        # Ensure end_date is after start_date
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError('End date must be after start date.')

    def __str__(self):
        return f'{self.id} - {self.user.email} - {self.medication_name}'

class ReminderTime(models.Model):
    reminder = models.ForeignKey(Reminder, related_name='times', on_delete=models.CASCADE)
    time = models.TimeField()
    dosage = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return f'{self.reminder.medication_name} - {str(self.time)} - {self.dosage}'



