from rest_framework import serializers
from .models import HandwritingAnalysisTable

class HandwritingAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = HandwritingAnalysisTable
        fields = ['id', 'image_url', 'recognized_text', 'analyzed_text', 'created_at']
        read_only_fields = ['recognized_text', 'analyzed_text', 'created_at']
