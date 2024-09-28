from django.db import models
from django.conf import settings
from django.utils import timezone

class Reminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    medication_name = models.CharField(max_length=255, null=False, blank=False)
    reason_for_medication = models.TextField(null=False, blank=False)
    
    FREQUENCY_CHOICES = [
        ('daily', 'Everyday'),
        ('every_x_days', 'Every X days'),
        ('day_of_week', 'Day of the week'),
        ('day_of_month', 'Day of the month'),
    ]
    
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES, default='daily', blank=False, null=False)
    time = models.TimeField(blank=False, null=False)
    dosage = models.CharField(max_length=100, blank=False,  null=False)
    
    # Duration only applies to specific frequencies
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    memo = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.email} - {self.medication_name}'

