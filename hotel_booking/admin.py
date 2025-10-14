from django.contrib import admin
from .models import Hotel, HotelImage, HotelBooking  # Remove HotelReview

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1
    fields = ['image', 'caption', 'is_primary']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'price_per_night', 'overall_rating', 'is_active', 'featured']
    list_filter = ['city', 'state', 'is_active', 'featured', 'created_at']
    search_fields = ['name', 'city', 'address', 'email']
    list_editable = ['is_active', 'featured']
    inlines = [HotelImageInline]
    readonly_fields = ['overall_rating', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'country', 'pincode')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Pricing', {
            'fields': ('price_per_night',)
        }),
        ('Ratings', {
            'fields': ('cleanliness_rating', 'comfort_rating', 'safety_rating', 'overall_rating'),
            'description': 'Overall rating is calculated automatically'
        }),
        ('Amenities', {
            'fields': ('wifi', 'parking', 'restaurant', 'pool', 'gym', 'spa', 'room_service', 'air_conditioning'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'hotel', 'check_in_date', 'check_out_date', 'nights', 'rooms', 'total_amount', 'booking_status']
    list_filter = ['booking_status', 'created_at', 'check_in_date']
    search_fields = ['booking_id', 'user__username', 'user__email', 'hotel__name', 'contact_email']
    readonly_fields = ['booking_id', 'nights', 'total_amount', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'user', 'hotel', 'booking_status')
        }),
        ('Stay Details', {
            'fields': ('check_in_date', 'check_out_date', 'nights', 'guests', 'rooms')
        }),
        ('Pricing', {
            'fields': ('price_per_night', 'total_amount')
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_phone', 'contact_email')
        }),
        ('Additional Details', {
            'fields': ('special_requests',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_confirmed', 'mark_cancelled', 'mark_completed']
    
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(booking_status='CONFIRMED')
        self.message_user(request, f'{updated} bookings marked as confirmed.')
    mark_confirmed.short_description = 'Mark selected bookings as Confirmed'
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(booking_status='CANCELLED')
        self.message_user(request, f'{updated} bookings marked as cancelled.')
    mark_cancelled.short_description = 'Mark selected bookings as Cancelled'
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(booking_status='COMPLETED')
        self.message_user(request, f'{updated} bookings marked as completed.')
    mark_completed.short_description = 'Mark selected bookings as Completed'

@admin.register(HotelImage)
class HotelImageAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'caption', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at', 'hotel']
    search_fields = ['hotel__name', 'caption']
    list_editable = ['is_primary']

# HotelReview is in review_feedback app - don't register here