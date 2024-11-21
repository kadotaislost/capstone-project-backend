from django.db import models
from django.conf import settings

class HandwritingAnalysisTable(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='handwriting_analyses', help_text="User who uploaded the image")
    prescription_name = models.CharField(max_length=100, help_text="Name of the prescription")
    image_url = models.URLField(max_length=500, help_text="URL of the uploaded image")
    recognized_text = models.TextField(help_text="Text recognized from the image")
    analyzed_text = models.TextField(help_text="Analyzed or processed text")

    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp of when the record was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp of when the record was last updated" , verbose_name="Updated At")

    def __str__(self):
        return f"Analysis for Image: {self.image_url}"

    class Meta:
        verbose_name = "Handwriting Analysis"
        verbose_name_plural = "Handwriting Analyses"
        ordering = ['-created_at']
