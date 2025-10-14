from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import random
import string

User = get_user_model()

class Route(models.Model):
    owner = models.ForeignKey('service_provider.ServiceProvider', on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_routes')
    TRANSPORT_TYPE = [
        ('FLIGHT', 'Flight'),
        ('TRAIN', 'Train'),
        ('BUS', 'Bus')
    ]
    
    # Basic route information
    transport_type = models.CharField(max_length=10, choices=TRANSPORT_TYPE)
    operator_name = models.CharField(max_length=200)
    route_number = models.CharField(max_length=50)  # Flight number, train number, bus number
    
    # Route details
    source_city = models.CharField(max_length=100)
    source_station = models.CharField(max_length=200)  # Airport, railway station, bus station
    destination_city = models.CharField(max_length=100)
    destination_station = models.CharField(max_length=200)
    
    # Timing
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    duration_hours = models.IntegerField()
    duration_minutes = models.IntegerField()
    
    # Days of operation
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=True)
    sunday = models.BooleanField(default=True)
    
    # Pricing and availability
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_seats = models.IntegerField()
    available_seats = models.IntegerField()
    
    # Features (especially for buses and trains)
    ac_available = models.BooleanField(default=False)
    sleeper_available = models.BooleanField(default=False)
    wifi_available = models.BooleanField(default=False)
    food_service = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def duration_display(self):
        return f"{self.duration_hours}h {self.duration_minutes}m"
    
    def __str__(self):
        return f"{self.route_number} - {self.source_city} to {self.destination_city}"
    
    class Meta:
        ordering = ['departure_time', 'base_price']

class TransportBooking(models.Model):
    BOOKING_STATUS = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
        ('NO_SHOW', 'No Show')
    ]
    
    CLASS_TYPE = [
        ('ECONOMY', 'Economy'),
        ('PREMIUM', 'Premium'),
        ('BUSINESS', 'Business'),
        ('FIRST', 'First Class')
    ]
    
    # Booking details
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    
    # Travel details
    travel_date = models.DateField()
    passengers = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    class_type = models.CharField(max_length=10, choices=CLASS_TYPE, default='ECONOMY')
    
    # Passenger details
    passenger_names = models.TextField()  # JSON format for multiple passengers
    passenger_ages = models.TextField()   # JSON format for ages
    passenger_genders = models.TextField() # JSON format for genders
    
    # Pricing
    price_per_ticket = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # Contact info
    contact_name = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=17)
    contact_email = models.EmailField()
    
    # Status and booking info
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='PENDING')
    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    seat_numbers = models.TextField(blank=True)  # Assigned seat numbers
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calculate total amount
        self.total_amount = self.price_per_ticket * self.passengers
        
        # Generate booking ID
        if not self.booking_id:
            prefix = {
                'FLIGHT': 'NMF',
                'TRAIN': 'NMT',
                'BUS': 'NMB'
            }.get(self.route.transport_type, 'NOM')
            self.booking_id = prefix + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.route.route_number}"
    
    class Meta:
        ordering = ['-created_at']

class RouteReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    booking = models.ForeignKey(TransportBooking, on_delete=models.CASCADE, null=True, blank=True)
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    punctuality_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comfort_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    service_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'route']
        ordering = ['-created_at']