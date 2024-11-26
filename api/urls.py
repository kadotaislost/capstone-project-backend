from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView
from .views import serve_custom_openapi_yaml



urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend-otp'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('password-reset-request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/<uid>/<token>/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('update-user-profile/', views.UserProfileView.as_view(), name='update-user-profile'),
    path('get-user-profile/', views.UserProfileView.as_view(), name='get-user-profile'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('search-medicine/', views.MedicineSearchView.as_view(), name='search-medicine'),
    
        # Serve the custom YAML file as the schema endpoint
    path("schema/", serve_custom_openapi_yaml, name="custom-schema"),
    # Swagger UI using the custom schema
    path("docs/", SpectacularSwaggerView.as_view(url_name="custom-schema"), name="swagger-ui"),
]

