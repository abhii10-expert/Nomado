from django.contrib import admin
from .models import Hotel, HotelImage, HotelBooking

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'price_per_night', 'overall_rating', 'is_active', 'featured']
    list_filter = ['city', 'is_active', 'featured', 'created_at']
    search_fields = ['name', 'city', 'address']
    list_editable = ['is_active', 'featured']
    inlines = [HotelImageInline]
    readonly_fields = ['overall_rating']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'address', 'city', 'state', 'country', 'pincode', 'phone', 'email', 'website')
        }),
        ('Pricing', {
            'fields': ('price_per_night',)
        }),
        ('Ratings', {
            'fields': ('cleanliness_rating', 'comfort_rating', 'safety_rating', 'overall_rating')
        }),
        ('Amenities', {
            'fields': ('wifi', 'parking', 'restaurant', 'pool', 'gym', 'spa', 'room_service', 'air_conditioning')
        }),
        ('Status', {
            'fields': ('is_active', 'featured')
        }),
    )

@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'hotel', 'check_in_date', 'check_out_date', 'total_amount', 'booking_status']
    list_filter = ['booking_status', 'created_at', 'check_in_date']
    search_fields = ['booking_id', 'user__username', 'hotel__name']
    readonly_fields = ['booking_id', 'nights', 'total_amount']
    date_hierarchy = 'created_at'