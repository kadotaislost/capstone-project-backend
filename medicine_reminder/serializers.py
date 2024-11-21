
from rest_framework import serializers
from .models import Reminder, ReminderTime
from datetime import datetime

class ReminderTimeSerializer(serializers.ModelSerializer):
    time = serializers.CharField()  # Accept and return time as a string in 12-hour format

    class Meta:
        model = ReminderTime
        fields = ['id', 'time', 'dosage', 'unit']

    def validate_time(self, value):
        try:
            # Convert 12-hour format (e.g., "02:30 PM") to 24-hour format
            return datetime.strptime(value, "%I:%M %p").time()
        except ValueError:
            raise serializers.ValidationError("Time must be in the format HH:MM AM/PM.")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert 24-hour format to 12-hour format for output
        representation['time'] = instance.time.strftime("%I:%M %p")
        return representation

class ReminderSerializer(serializers.ModelSerializer):
    times = ReminderTimeSerializer(many=True)
    class Meta:
        model = Reminder
        fields = ['id', 'medication_name', 'reason_for_medication', 'frequency', 'start_date', 'end_date', 'memo','created_at', 'updated_at', 'times', 'every_x_days', 'day_of_week', 'day_of_month']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        # Validate frequency-specific fields
        frequency = data.get('frequency')
        if frequency == 'day_of_week' and not data.get('day_of_week'):
            raise serializers.ValidationError("day of week is required for this frequency.")
        elif frequency == 'day_of_month' and not data.get('day_of_month'):
            raise serializers.ValidationError("day of month is required for this frequency.")
        elif frequency == 'every_x_days' and not data.get('every_x_days'):
            raise serializers.ValidationError("every x days is required for this frequency.")

        # Validate end_date
        if data.get('end_date') and data['end_date'] <= data['start_date']:
            raise serializers.ValidationError({"error": "End date must be after start date."})

        return data

    def create(self, validated_data):
        times_data = validated_data.pop('times', [])
        reminder = Reminder.objects.create(**validated_data)
        for time_data in times_data:
            ReminderTime.objects.create(reminder=reminder, **time_data)
        return reminder

    def update(self, instance, validated_data):
        times_data = validated_data.pop('times', [])
        instance = super().update(instance, validated_data)

        # Update or create ReminderTime instances
        existing_time_objects = instance.times.all()
        existing_times = {}
        for time in existing_time_objects:
            existing_times[time.id] = time
            
        for time_data in times_data:
            time_id = time_data.get('id')
            if time_id:
                if time_id in existing_times:
                    self.update_reminder_time(existing_times[time_id], time_data)
                    del existing_times[time_id] 
            else:
                ReminderTime.objects.create(reminder=instance, **time_data)
        
        # Delete any remaining times
        for time in existing_times.values():
            time.delete()

        return instance

    def update_reminder_time(self, instance, data):
        instance.time = data.get('time', instance.time)
        instance.dosage = data.get('dosage', instance.dosage)
        instance.save()