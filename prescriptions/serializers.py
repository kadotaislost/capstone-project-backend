from rest_framework import serializers
from .models import HandwritingAnalysisTable

class HandwritingAnalysisSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = HandwritingAnalysisTable
        fields = ['id', 'image_url','prescription_name', 'recognized_text', 'analyzed_text', 'user', 'created_at']
        read_only_fields = ['created_at']

    def validate_image_url(self, value):
        """
        Validate the `image_url` field to ensure it is a valid URL.
        """
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Invalid image URL. It must start with 'http://' or 'https://'.")
        return value

    def create(self, validated_data):
        """
        Custom create method to handle additional fields.
        """
        return HandwritingAnalysisTable.objects.create(**validated_data)
