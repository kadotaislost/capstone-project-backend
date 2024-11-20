from django.urls import path

from . import views

urlpatterns = [
    path('analyze_image/', views.HandwritingAnalysisView.as_view(), name='handwriting_recognition'),
    path('prescriptions/', views.UserPrescriptionsView.as_view(), name='prescriptions'),
    path('prescriptions/<int:prescription_id>/', views.PrescriptionDetailView.as_view(), name='prescription-detail'),
]
