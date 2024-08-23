from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer , EmailVerificationSerializer , LoginSerializer, ChangePasswordSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, UserUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from .models import EmailVerification
from django.utils.encoding import force_bytes , force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({"message": "User registered successfully. Please verify your email to activate the account.", "token": token}, status=status.HTTP_201_CREATED)
 

# Email Verification View
class VerifyEmailView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Raise exception if invalid
        serializer.save()
        return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)

# Resend OTP View
class ResendOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            verification = EmailVerification.objects.get(user=user)
            verification.refresh_otp()
            
            send_mail(
                'Your New Email Verification Code',
                f'Your new OTP code is {verification.otp}',
                'prescriptaidnepal@gmail.com',
                [user.email],
                fail_silently=False,
            )
            
            return Response({"message": "New OTP sent successfully."}, status=status.HTTP_200_OK)
        except EmailVerification.DoesNotExist:
            return Response({"error": "No verification process found for this user."}, status=status.HTTP_400_BAD_REQUEST)

# User Login View
class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Raise exception if invalid
        user = serializer.validated_data['user']
        token = get_tokens_for_user(user)
        return Response({'message': "Login Successful!", 'token': token}, status=status.HTTP_200_OK)

# Change Password View
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)  # Raise exception if invalid
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
    
class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        link = f"http://localhost:3000/password-reset-request/{uid}/{token}"
        
        send_mail(
            'Password Reset Request',
            f'Please click on the link below to reset your password: {link}',
            'prescriptaidnepal@gmail.com',
            [user.email],
            fail_silently=False,
        )
        
        return Response({"message": "Password reset link sent successfully. Please check your email."}, status=status.HTTP_200_OK)
        
            
class PasswordResetConfirmView(APIView):
    def post(self, request, uid, token):
        serializer = PasswordResetConfirmSerializer(data=request.data , context = {'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserUpdateSerializer(request.user , context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    