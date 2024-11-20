from django.contrib import admin
from .models import HandwritingAnalysisTable

@admin.register(HandwritingAnalysisTable)
class HandwritingRecognitionAdmin(admin.ModelAdmin):
    list_display = ['image_url', 'recognized_text', 'analyzed_text',]
