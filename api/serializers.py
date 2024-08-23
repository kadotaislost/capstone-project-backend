from rest_framework import serializers
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
import random , string
from .models import EmailVerification
from django.contrib.auth import authenticate
from django.utils.encoding import force_bytes , force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number', 'blood_group', 'dob', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        try:
            validate_password(data['password'])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        otp_code = ''.join(random.choices(string.digits, k=4))
        EmailVerification.objects.create(user=user, otp=otp_code)
        send_mail(
            'Your Email Verification Code',
            f'Thank you for registering for PrescriptAid. Your OTP code is {otp_code}',
            'prescriptaidnepal@gmail.com',
            [user.email],
            fail_silently=False,
        )
        
        
class EmailVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=4)
    
    def validate(self, data):
        otp_code = data.get('otp')
        try: 
            verification = EmailVerification.objects.get(otp=otp_code)
            if verification.is_expired():
                raise serializers.ValidationError("The OTP code has expired. Please request a new one.")
            
            user = verification.user
            if user.email_verified:
                raise serializers.ValidationError("Email already verified")
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP code.")
        
        return data
    
    def save(self):
        otp_code = self.validated_data['otp']
        verification = EmailVerification.objects.get(otp=otp_code)
        user = verification.user
        user.email_verified = True  # Activate the user
        user.save()
        verification.delete()
        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email is None or password is None:
            raise serializers.ValidationError("Both email and password are required.")

        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid Credentials.")

        if not user.email_verified:
            raise serializers.ValidationError("Email is not verified. Please verify your email to log in.")

        data['user'] = user
        return data
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("New passwords do not match")
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("New password cannot be the same as the old password")
        try:
            validate_password(data['new_password'], self.context['request'].user)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})      
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
  
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        new_password = data['new_password']
        confirm_new_password = data['confirm_new_password']
        uid = self.context['uid']
        token = self.context['token']
        
        if new_password != confirm_new_password:
            raise serializers.ValidationError("Passwords do not match")
        
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(id=uid)
        try:
            validate_password(new_password, user)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Invalid or expired token")
        
        user.set_password(new_password)
        user.save()
        return data
    
class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number', 'blood_group', 'dob', 'profile_pic']
    

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.blood_group = validated_data.get('blood_group', instance.blood_group)
        instance.dob = validated_data.get('dob', instance.dob)
        if 'profile_pic' in validated_data:
            instance.profile_pic = validated_data.get('profile_pic', instance.profile_pic)
        instance.save()
        return instance
    