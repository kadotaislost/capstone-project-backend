from django.urls import path

from . import views

urlpatterns = [
    path('analyze_image/', views.HandwritingAnalysisView.as_view(), name='handwriting_recognition'),
]
