from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class ServiceProvider(models.Model):
    PROVIDER_TYPE = [
        ('HOTEL', 'Hotel Owner'),
        ('TRANSPORT', 'Transport Operator'),
        ('BOTH', 'Both Hotel & Transport'),
    ]
    
    VERIFICATION_STATUS = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPE)
    
    # Business details
    business_name = models.CharField(max_length=200)
    business_registration_number = models.CharField(max_length=50)
    gst_number = models.CharField(max_length=15, blank=True)
    
    # Contact information
    business_phone = models.CharField(max_length=17)
    business_email = models.EmailField()
    business_address = models.TextField()
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='PENDING')
    verification_documents = models.FileField(upload_to='verification_docs/', blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_providers')
    
    # Banking details
    bank_account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    bank_ifsc_code = models.CharField(max_length=11)
    account_holder_name = models.CharField(max_length=100)
    
    # Commission and earnings
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)  # Percentage
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business_name} ({self.user.username})"

class ProviderNotification(models.Model):
    NOTIFICATION_TYPE = [
        ('BOOKING', 'New Booking'),
        ('CANCELLATION', 'Booking Cancellation'),
        ('PAYMENT', 'Payment Received'),
        ('REVIEW', 'New Review'),
        ('SYSTEM', 'System Notification'),
    ]
    
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    hotel_booking = models.ForeignKey('hotel_booking.HotelBooking', on_delete=models.CASCADE, null=True, blank=True)
    transport_booking = models.ForeignKey('transportation.TransportBooking', on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class ProviderEarnings(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='earnings')
    
    # Booking reference
    hotel_booking = models.ForeignKey('hotel_booking.HotelBooking', on_delete=models.CASCADE, null=True, blank=True)
    transport_booking = models.ForeignKey('transportation.TransportBooking', on_delete=models.CASCADE, null=True, blank=True)
    
    # Financial details
    booking_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    provider_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    is_settled = models.BooleanField(default=False)
    settled_at = models.DateTimeField(null=True, blank=True)
    settlement_reference = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']