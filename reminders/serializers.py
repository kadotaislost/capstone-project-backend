from rest_framework import serializers
from .models import Reminder

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id', 'medication_name', 'reason_for_medication', 'frequency', 'time', 'dosage', 'start_date', 'end_date', 'memo', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
       
    def validate(self, data):
        frequency = data.get('frequency')
        required_fields = ['medication_name', 'reason_for_medication', 'frequency', 'time', 'dosage']
        
        if frequency in ['daily', 'every_x_days']:
            required_fields.extend(['start_date', 'end_date'])
               
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: f"{field.replace('_', ' ').capitalize()} is required."})
        
        if data.get('start_date') and data.get('end_date') and data['start_date'] > data['end_date']:
            raise serializers.ValidationError({"end_date": "End date must be after start date."})
        
        return data
            
        
