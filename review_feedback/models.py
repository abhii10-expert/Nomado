from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class HotelReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey('hotel_booking.Hotel', on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField('hotel_booking.HotelBooking', on_delete=models.CASCADE, null=True, blank=True)
    
    # Ratings (1-5 scale)
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    cleanliness_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comfort_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    service_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    value_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    location_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Review content
    title = models.CharField(max_length=200)
    review_text = models.TextField()
    
    # Additional info
    stayed_date = models.DateField(null=True, blank=True)
    room_type = models.CharField(max_length=100, blank=True)
    
    # Helpful votes
    helpful_votes = models.IntegerField(default=0)
    
    # Status
    is_verified = models.BooleanField(default=False)  # If user actually stayed
    is_approved = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'hotel']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.hotel.name}"

class TransportReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    route = models.ForeignKey('transportation.Route', on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField('transportation.TransportBooking', on_delete=models.CASCADE, null=True, blank=True)
    
    # Ratings (1-5 scale)
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    punctuality_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comfort_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    service_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    value_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Review content
    title = models.CharField(max_length=200)
    review_text = models.TextField()
    
    # Additional info
    travel_date = models.DateField(null=True, blank=True)
    
    # Helpful votes
    helpful_votes = models.IntegerField(default=0)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'route']
        ordering = ['-created_at']

class ReviewHelpful(models.Model):
    """Track which users found reviews helpful"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel_review = models.ForeignKey(HotelReview, on_delete=models.CASCADE, null=True, blank=True)
    transport_review = models.ForeignKey(TransportReview, on_delete=models.CASCADE, null=True, blank=True)
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ['user', 'hotel_review'],
            ['user', 'transport_review'],
        ]

class Feedback(models.Model):
    FEEDBACK_TYPE = [
        ('BUG', 'Bug Report'),
        ('FEATURE', 'Feature Request'),
        ('COMPLAINT', 'Complaint'),
        ('SUGGESTION', 'Suggestion'),
        ('COMPLIMENT', 'Compliment'),
        ('OTHER', 'Other'),
    ]
    
    FEEDBACK_STATUS = [
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Contact info
    email = models.EmailField()
    phone = models.CharField(max_length=17, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=FEEDBACK_STATUS, default='NEW')
    priority = models.CharField(max_length=10, choices=[
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ], default='MEDIUM')
    
    # Admin response
    admin_response = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback_responses')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.feedback_type}: {self.subject}"