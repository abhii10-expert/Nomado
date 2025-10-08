from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    is_service_provider = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    travel_preferences = models.TextField(blank=True)
    preferred_budget = models.CharField(max_length=20, choices=[
        ('BUDGET', 'Budget (Under $50)'),
        ('MID', 'Mid-range ($50-$150)'),
        ('LUXURY', 'Luxury ($150+)')
    ], default='MID')
    notification_enabled = models.BooleanField(default=True)
    location_sharing_enabled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"