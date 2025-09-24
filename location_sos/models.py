from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class EmergencyContact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('FAMILY', 'Family Member'),
        ('FRIEND', 'Friend'),
        ('COLLEAGUE', 'Colleague'),
        ('SPOUSE', 'Spouse'),
        ('PARENT', 'Parent'),
        ('SIBLING', 'Sibling'),
        ('RELATIVE', 'Relative'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    email = models.EmailField()  # Made required, removed phone number
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Ensure only one primary contact per user
        if self.is_primary:
            EmergencyContact.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    class Meta:
        ordering = ['-is_primary', 'name']

class LocationShare(models.Model):
    SHARE_STATUS = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('STOPPED', 'Stopped'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_shares')
    share_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Location data
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    address = models.TextField(blank=True)
    accuracy = models.FloatField(null=True, blank=True)  # GPS accuracy in meters
    
    # Sharing details
    shared_with_contacts = models.ManyToManyField(EmergencyContact, blank=True)
    shared_with_email = models.EmailField(blank=True)  # Changed from phone to email
    message = models.TextField(blank=True)
    
    # Duration and status
    duration_hours = models.IntegerField(default=1)  # How long to share for
    status = models.CharField(max_length=10, choices=SHARE_STATUS, default='ACTIVE')
    
    # Email notification tracking
    emails_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Location share by {self.user.username} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']

class SOSAlert(models.Model):
    ALERT_STATUS = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('RESOLVED', 'Resolved'),
        ('FALSE_ALARM', 'False Alarm'),
    ]
    
    ALERT_TYPE = [
        ('EMERGENCY', 'Emergency'),
        ('MEDICAL', 'Medical Emergency'),
        ('SECURITY', 'Security Threat'),
        ('ACCIDENT', 'Accident'),
        ('LOST', 'Lost/Stranded'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sos_alerts')
    alert_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Location data
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    address = models.TextField(blank=True)
    
    # Alert details
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE, default='EMERGENCY')
    message = models.TextField(blank=True)
    
    # Status and response
    status = models.CharField(max_length=20, choices=ALERT_STATUS, default='ACTIVE')
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Email notification tracking (removed phone fields)
    emails_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"SOS Alert {self.alert_id} by {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']

class SafetyCheckIn(models.Model):
    CHECK_STATUS = [
        ('SAFE', 'Safe'),
        ('CONCERN', 'Concern'),
        ('EMERGENCY', 'Emergency'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='safety_checkins')
    
    # Location data
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    address = models.TextField(blank=True)
    
    # Check-in details
    status = models.CharField(max_length=20, choices=CHECK_STATUS, default='SAFE')
    message = models.TextField(blank=True)
    
    # Email notification tracking
    emails_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Auto check-in settings
    is_scheduled = models.BooleanField(default=False)
    next_checkin_due = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Safety check-in by {self.user.username} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']

class TrustedContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trusted_contacts')
    trusted_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trusted_by')
    
    # Permissions
    can_see_location = models.BooleanField(default=True)
    can_receive_sos = models.BooleanField(default=True)
    can_receive_checkins = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    accepted = models.BooleanField(default=False)  # Whether the trusted user accepted
    
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'trusted_user']
    
    def __str__(self):
        return f"{self.user.username} trusts {self.trusted_user.username}"