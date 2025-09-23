from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'is_service_provider')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'date_of_birth', 'emergency_contact_name', 'emergency_contact_phone', 'is_service_provider')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile)