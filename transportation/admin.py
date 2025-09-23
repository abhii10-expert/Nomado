from django.contrib import admin
from .models import Route, TransportBooking, RouteReview

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['route_number', 'operator_name', 'transport_type', 'source_city', 'destination_city', 'base_price', 'available_seats', 'is_active']
    list_filter = ['transport_type', 'source_city', 'destination_city', 'is_active']
    search_fields = ['route_number', 'operator_name', 'source_city', 'destination_city']
    list_editable = ['is_active', 'available_seats']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('transport_type', 'operator_name', 'route_number')
        }),
        ('Route Details', {
            'fields': ('source_city', 'source_station', 'destination_city', 'destination_station')
        }),
        ('Timing', {
            'fields': ('departure_time', 'arrival_time', 'duration_hours', 'duration_minutes')
        }),
        ('Days of Operation', {
            'fields': ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
        }),
        ('Pricing & Availability', {
            'fields': ('base_price', 'total_seats', 'available_seats')
        }),
        ('Features', {
            'fields': ('ac_available', 'sleeper_available', 'wifi_available', 'food_service')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(TransportBooking)
class TransportBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'route', 'travel_date', 'passengers', 'total_amount', 'booking_status']
    list_filter = ['booking_status', 'route__transport_type', 'created_at', 'travel_date']
    search_fields = ['booking_id', 'user__username', 'route__route_number']
    readonly_fields = ['booking_id', 'total_amount']
    date_hierarchy = 'created_at'

@admin.register(RouteReview)
class RouteReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'route', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'route__transport_type']
    search_fields = ['user__username', 'route__route_number']