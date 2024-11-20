from django.urls import path

from . import views

urlpatterns = [
    path('analyze_image/', views.HandwritingAnalysisView.as_view(), name='handwriting_recognition'),
    path('get_all_prescriptions/', views.UserPrescriptionsView.as_view(), name='get_all_prescriptions'),
]
