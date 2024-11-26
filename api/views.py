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
from django.contrib.auth.tokens import default_token_generator
import google.generativeai as genai
import re
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import  HttpResponse
import yaml

User = get_user_model()

def serve_custom_openapi_yaml(request):
    with open("openapi.yaml", "r") as file:
        return HttpResponse(file.read(), content_type="application/yaml")

# User Registration View
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
                'Your New OTP Code for Email Verification - PrescriptAid',
                f'''
Dear {user.full_name},

We noticed that you requested a new One-Time Password (OTP) to verify your email address. Please find your new OTP below:

Your New OTP Code: {verification.otp}

This code will expire in 5 minutes. If you did not request a new OTP, please ignore this email or reach out to our support team for assistance.

Thank you for choosing PrescriptAid!

Best regards,
The PrescriptAid Team
                ''',
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
        token = default_token_generator.make_token(user)
        link = f"http://localhost:8000/password-reset-request/{uid}/{token}"
                
        send_mail(
            'Reset Your Password for PrescriptAid',
            f'''
Dear {user.full_name},

We received a request to reset your password for your PrescriptAid account. To proceed, please click the link below:

Reset Password Link: {link}

This link is valid for the next 15 minutes. If you did not request a password reset, please disregard this email.

Stay safe,
The PrescriptAid Team
            ''',
            'prescriptaidnepal@gmail.com',
            [user.email],
            fail_silently=False,
        )
        
        return Response({"message": "Password reset link sent successfully. Please check your email."}, status=status.HTTP_200_OK)
        
            
class PasswordResetConfirmView(APIView):
    def post(self, request, uid, token):
        serializer = PasswordResetConfirmSerializer(data=request.data , context = {'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        serializer.save()
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

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
        
class MedicineSearchView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Get medicine name from query parameters
        medicine_name = request.query_params.get('medicine', None)

        if not medicine_name:
            return Response({"error": "Medicine name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Query Gemini API for the medicine information
        medicine_info = self.query_gemini(medicine_name)
        print(medicine_info)
        if medicine_info:
            structured_info = self.parse_medicine_info(medicine_info)
            return Response(structured_info, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Unable to find information for the given medicine"}, status=status.HTTP_404_NOT_FOUND)

    def query_gemini(self, medicine_name):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        prompt = f"""
        You are a helpful medical information assistant. Your task is to provide factual information about the medicine {medicine_name} in a structured format. Present the information in the following sections, using only verified medical sources:

        Description:
        [Provide a brief, factual overview of {medicine_name}, including its drug class and basic function.]

        Uses:
        [List the primary medical uses of {medicine_name}, focusing on conditions it's commonly prescribed for.]

        Side Effects:
        [Enumerate the most common side effects of {medicine_name}. If there are serious side effects, briefly mention them as well.]

        Drug Interactions:
        [List any significant known drug interactions with {medicine_name}.]

        Important Notes:
        - If information for any section is unavailable or uncertain, state "Information not available" for that section.
        - Do not speculate or provide medical advice.
        - Include a disclaimer at the end stating: "This information is for educational purposes only and should not replace professional medical advice. Always consult a healthcare provider before using any medication."

        Respond only with the requested information in the structure provided above. Do not add any additional commentary or advice.
        """

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error querying Gemini API: {str(e)}")
        return None

    def parse_medicine_info(self, response_text):
        # Regular expressions to capture each section
        description_match = re.search(r"Description:(.*?)(Uses:|Side Effects:|Drug Interactions:|$)", response_text, re.S)
        uses_match = re.search(r"Uses:(.*?)(Side Effects:|Drug Interactions:|Description:|$)", response_text, re.S)
        side_effects_match = re.search(r"Side Effects:(.*?)(Drug Interactions:|Uses:|Description:|$)", response_text, re.S)
        interactions_match = re.search(r"Drug Interactions:(.*?)(Uses:|Side Effects:|Description:|$)", response_text, re.S)

        # Extracting text, stripping unnecessary whitespace and cleaning up unwanted characters
        description = self.clean_text(description_match.group(1)) if description_match else None
        uses = self.clean_text(uses_match.group(1)) if uses_match else None
        side_effects = self.clean_text(side_effects_match.group(1)) if side_effects_match else None
        drug_interactions = self.clean_text(interactions_match.group(1)) if interactions_match else None
        
        # Structuring the response
        return {
            "description": description,
            "uses": uses,
            "side_effects": side_effects,
            "drug_interactions": drug_interactions
        }


    def clean_text(self, text):
        """Utility function to clean and format text."""
        if text:
            # Remove leading and trailing spaces
            text = text.strip()
            
            # Remove unwanted characters and symbols
            text = text.replace('**', '')  # Remove asterisks
            
            # Remove bullet points and extra newlines
            text = re.sub(r'\*\s*', '', text)  # Remove bullet points
            text = re.sub(r'\n+', ' ', text)  # Replace multiple newlines with a single space
            
            # Replace multiple spaces with a single space
            text = re.sub(r'\s+', ' ', text)
            
            # Optionally, remove extra leading and trailing spaces after all replacements
            text = text.strip()
            
            # Capitalize the first letter of each section for better readability (optional)
            text = re.sub(r'(\. )(\w)', lambda m: m.group(1) + m.group(2).upper(), text)
        
        return text

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }