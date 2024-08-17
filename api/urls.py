from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='verify'),
     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
