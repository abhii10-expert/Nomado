from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=17)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Pricing
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Ratings (1-5 scale)
    cleanliness_rating = models.FloatField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    comfort_rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    safety_rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    overall_rating = models.FloatField(default=0, editable=False)
    
    # Amenities
    wifi = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    restaurant = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    spa = models.BooleanField(default=False)
    room_service = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calculate overall rating
        ratings = [self.cleanliness_rating, self.comfort_rating, self.safety_rating]
        self.overall_rating = sum(ratings) / len([r for r in ratings if r > 0]) if any(ratings) else 0
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    class Meta:
        ordering = ['-overall_rating', '-featured', 'name']

class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hotels/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.hotel.name} - Image"

class HotelBooking(models.Model):
    BOOKING_STATUS = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
        ('NO_SHOW', 'No Show')
    ]
    
    # Booking details
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    
    # Dates and guests
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    nights = models.IntegerField(editable=False)
    guests = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    rooms = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Pricing
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # Status and details
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='PENDING')
    special_requests = models.TextField(blank=True)
    
    # Contact info
    contact_name = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=17)
    contact_email = models.EmailField()
    
    # Timestamps
    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calculate nights and total amount
        if self.check_in_date and self.check_out_date:
            self.nights = (self.check_out_date - self.check_in_date).days
            self.total_amount = self.price_per_night * self.nights * self.rooms
        
        # Generate booking ID
        if not self.booking_id:
            import random
            import string
            self.booking_id = 'NOM' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.hotel.name}"
    
    class Meta:
        ordering = ['-created_at']