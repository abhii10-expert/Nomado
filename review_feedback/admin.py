from django.contrib import admin
from .models import HotelReview, TransportReview, ReviewHelpful, Feedback

@admin.register(HotelReview)
class HotelReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'hotel', 'overall_rating', 'is_verified', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['overall_rating', 'is_verified', 'is_approved', 'is_featured', 'created_at']
    search_fields = ['user__username', 'hotel__name', 'title', 'review_text']
    list_editable = ['is_approved', 'is_featured']
    readonly_fields = ['helpful_votes', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'hotel', 'booking')
        }),
        ('Ratings', {
            'fields': ('overall_rating', 'cleanliness_rating', 'comfort_rating', 'service_rating', 'value_rating', 'location_rating')
        }),
        ('Review Content', {
            'fields': ('title', 'review_text', 'stayed_date', 'room_type')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_approved', 'is_featured', 'helpful_votes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_reviews', 'feature_reviews', 'verify_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved.')
    approve_reviews.short_description = 'Approve selected reviews'
    
    def feature_reviews(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} reviews featured.')
    feature_reviews.short_description = 'Feature selected reviews'
    
    def verify_reviews(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} reviews verified.')
    verify_reviews.short_description = 'Verify selected reviews'

@admin.register(TransportReview)
class TransportReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'route', 'overall_rating', 'is_verified', 'is_approved', 'created_at']
    list_filter = ['overall_rating', 'is_verified', 'is_approved', 'created_at']
    search_fields = ['user__username', 'route__route_number', 'title', 'review_text']
    list_editable = ['is_approved']
    readonly_fields = ['helpful_votes', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'route', 'booking')
        }),
        ('Ratings', {
            'fields': ('overall_rating', 'punctuality_rating', 'comfort_rating', 'service_rating', 'value_rating')
        }),
        ('Review Content', {
            'fields': ('title', 'review_text', 'travel_date')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_approved', 'helpful_votes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'feedback_type', 'subject', 'status', 'priority', 'created_at']
    list_filter = ['feedback_type', 'status', 'priority', 'created_at']
    search_fields = ['user__username', 'subject', 'message', 'email']
    list_editable = ['status', 'priority']
    readonly_fields = ['created_at', 'updated_at', 'responded_at']
    
    fieldsets = (
        ('Feedback Details', {
            'fields': ('user', 'feedback_type', 'subject', 'message')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Status', {
            'fields': ('status', 'priority')
        }),
        ('Admin Response', {
            'fields': ('admin_response', 'responded_by', 'responded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['user', 'hotel_review', 'transport_review', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['user__username']