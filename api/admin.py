from django.contrib import admin
from .models import User, EmailVerification
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.

class UserAdmin(BaseUserAdmin):
    list_display = ["id",'email', 'full_name', 'dob', 'blood_group', 'created_at', 'updated_at', 'is_active', 'is_superuser', 'email_verified']
    search_fields = ['email', 'full_name', 'phone_number']
    filter_horizontal = []
    ordering = ["email", 'full_name']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'email_verified']
    fieldsets = (
        ('User Credentials', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone_number', 'dob', 'blood_group', 'profile_pic')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'email_verified')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )
    
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "full_name", "phone_number","password1", "password2"],
            },
        ),
    ]
    
    readonly_fields = ('created_at', 'updated_at')
    
admin.site.register(User, UserAdmin) 
admin.site.register(EmailVerification)  
