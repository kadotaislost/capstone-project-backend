from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone
import datetime

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, password= None, phone_number= None, blood_group = None, dob = None):
    
        if not email:
            raise ValueError("The Email field must be set to a valid email address")
        
        if not full_name:
            raise ValueError("The Full Name field must be set")

        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            full_name=full_name ,
            phone_number = phone_number,
            blood_group = blood_group,
            dob = dob
        )
        
        if password:
            user.set_password(password)
        else:
            raise ValueError("Password must be set")
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None):
    
        user = self.create_user(
            email,
            password=password,
            full_name=full_name,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=3, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    def __str__(self):
        return f'{self.email} - {self.full_name}'
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
