from django.contrib import admin
from .models import Reminder
# Register your models here.

class ReminderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','medication_name', 'frequency', 'time', 'dosage', 'start_date', 'end_date']

admin.site.register(Reminder, ReminderAdmin)