from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid
import random
import string

User = get_user_model()

class PaymentMethod(models.Model):
    PAYMENT_TYPE = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('UPI', 'UPI'),
        ('NET_BANKING', 'Net Banking'),
        ('WALLET', 'Digital Wallet'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    
    # Card details (encrypted in real app)
    card_number = models.CharField(max_length=20, blank=True)  # Last 4 digits only
    card_holder_name = models.CharField(max_length=100, blank=True)
    expiry_month = models.CharField(max_length=2, blank=True)
    expiry_year = models.CharField(max_length=4, blank=True)
    
    # UPI details
    upi_id = models.CharField(max_length=100, blank=True)
    
    # Wallet details
    wallet_provider = models.CharField(max_length=50, blank=True)
    
    # Bank details
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, blank=True)  # Last 4 digits only
    
    # Status
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.is_default:
            PaymentMethod.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.payment_type in ['CREDIT_CARD', 'DEBIT_CARD']:
            return f"{self.payment_type} ending in {self.card_number[-4:]}"
        elif self.payment_type == 'UPI':
            return f"UPI: {self.upi_id}"
        else:
            return f"{self.payment_type}"

class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('HOTEL_BOOKING', 'Hotel Booking'),
        ('TRANSPORT_BOOKING', 'Transport Booking'),
        ('REFUND', 'Refund'),
        ('CANCELLATION', 'Cancellation Fee'),
    ]
    
    TRANSACTION_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    # Basic transaction details
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    
    # Related bookings
    hotel_booking = models.ForeignKey('hotel_booking.HotelBooking', on_delete=models.SET_NULL, null=True, blank=True)
    transport_booking = models.ForeignKey('transportation.TransportBooking', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Payment details
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    payment_gateway = models.CharField(max_length=50, default='Razorpay')
    gateway_transaction_id = models.CharField(max_length=100, blank=True)
    
    # Status and timing
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='PENDING')
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional info
    failure_reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
    
    class Meta:
        ordering = ['-initiated_at']

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    
    # Invoice details
    invoice_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = 'NOM' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"

class Refund(models.Model):
    REFUND_STATUS = [
        ('REQUESTED', 'Requested'),
        ('PROCESSING', 'Processing'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]
    
    refund_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='refunds')
    
    # Refund details
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=REFUND_STATUS, default='REQUESTED')
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Admin notes
    admin_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Refund {self.refund_id} - {self.status}"
    
    class Meta:
        ordering = ['-requested_at']