from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer , EmailVerificationSerializer , LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from .models import EmailVerification



# Create your views here.
class UserRegisterView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({"message": "User registered successfully. Please verify your email to activate the account." , "token": token}, status=status.HTTP_201_CREATED) 
          
class VerifyEmailView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
        
class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = get_tokens_for_user(user)
            return Response({'message': "Login Successful!",'token': token}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
          
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    