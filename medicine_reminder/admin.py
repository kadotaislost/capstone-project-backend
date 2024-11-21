from django.contrib import admin
from .models import Reminder, ReminderTime
# Register your models here.

class ReminderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','medication_name', 'frequency','repeat','start_date', 'end_date']
    fieldsets = (
        ('Reminder Details', {'fields': ('user', 'medication_name', 'reason_for_medication', 'frequency', 'every_x_days', 'day_of_week', 'day_of_month','start_date', 'end_date', 'memo', 'repeat')}),
    )
    
    
class ReminderTimeAdmin(admin.ModelAdmin):
    list_display = ['time', 'dosage', 'reminder', 'unit']
    fieldsets = (
        ('Reminder Time Details', {'fields': ('reminder', 'time', 'dosage' ,'unit')}),
    )

admin.site.register(Reminder, ReminderAdmin)
admin.site.register(ReminderTime, ReminderTimeAdmin)



