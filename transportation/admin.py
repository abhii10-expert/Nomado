from django.contrib import admin
from .models import Route, TransportBooking, RouteReview

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['route_number', 'operator_name', 'transport_type', 'source_city', 'destination_city', 'departure_time', 'base_price', 'available_seats', 'is_active']
    list_filter = ['transport_type', 'source_city', 'destination_city', 'is_active', 'created_at']
    search_fields = ['route_number', 'operator_name', 'source_city', 'destination_city', 'source_station', 'destination_station']
    list_editable = ['is_active', 'available_seats']
    readonly_fields = ['created_at']
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('transport_type', 'operator_name', 'route_number')
        }),
        ('Route Details', {
            'fields': ('source_city', 'source_station', 'destination_city', 'destination_station')
        }),
        ('Timing', {
            'fields': ('departure_time', 'arrival_time', 'duration_hours', 'duration_minutes'),
            'description': 'Enter duration in hours and minutes'
        }),
        ('Days of Operation', {
            'fields': ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'),
            'classes': ('collapse',)
        }),
        ('Pricing & Availability', {
            'fields': ('base_price', 'total_seats', 'available_seats')
        }),
        ('Features', {
            'fields': ('ac_available', 'sleeper_available', 'wifi_available', 'food_service'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )
    
    actions = ['activate_routes', 'deactivate_routes', 'reset_available_seats']
    
    def activate_routes(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} routes activated.')
    activate_routes.short_description = 'Activate selected routes'
    
    def deactivate_routes(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} routes deactivated.')
    deactivate_routes.short_description = 'Deactivate selected routes'
    
    def reset_available_seats(self, request, queryset):
        for route in queryset:
            route.available_seats = route.total_seats
            route.save()
        self.message_user(request, f'{queryset.count()} routes had seats reset.')
    reset_available_seats.short_description = 'Reset available seats to total seats'

@admin.register(TransportBooking)
class TransportBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'route', 'travel_date', 'passengers', 'class_type', 'total_amount', 'booking_status']
    list_filter = ['booking_status', 'route__transport_type', 'class_type', 'created_at', 'travel_date']
    search_fields = ['booking_id', 'user__username', 'user__email', 'route__route_number', 'contact_email']
    readonly_fields = ['booking_id', 'total_amount', 'created_at', 'updated_at']
    date_hierarchy = 'travel_date'
    list_per_page = 25
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'user', 'route', 'booking_status')
        }),
        ('Travel Details', {
            'fields': ('travel_date', 'passengers', 'class_type', 'seat_numbers')
        }),
        ('Passenger Information', {
            'fields': ('passenger_names', 'passenger_ages', 'passenger_genders'),
            'description': 'Store as JSON format'
        }),
        ('Pricing', {
            'fields': ('price_per_ticket', 'total_amount')
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_phone', 'contact_email')
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

@admin.register(RouteReview)
class RouteReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'route', 'rating', 'punctuality_rating', 'comfort_rating', 'service_rating', 'created_at']
    list_filter = ['rating', 'created_at', 'route__transport_type']
    search_fields = ['user__username', 'route__route_number', 'review_text']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Review Information', {
            'fields': ('user', 'route', 'booking')
        }),
        ('Ratings', {
            'fields': ('rating', 'punctuality_rating', 'comfort_rating', 'service_rating')
        }),
        ('Review Text', {
            'fields': ('review_text',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )