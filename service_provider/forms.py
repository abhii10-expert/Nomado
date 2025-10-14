from django import forms
from hotel_booking.models import Hotel, HotelImage
from transportation.models import Route
from .models import ServiceProvider

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = [
            'name', 'description', 'address', 'city', 'state', 'country', 'pincode',
            'phone', 'email', 'website', 'price_per_night',
            'wifi', 'parking', 'restaurant', 'pool', 'gym', 'spa', 'room_service', 'air_conditioning'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'value': 'India'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class HotelImageForm(forms.ModelForm):
    class Meta:
        model = HotelImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = [
            'transport_type', 'operator_name', 'route_number',
            'source_city', 'source_station', 'destination_city', 'destination_station',
            'departure_time', 'arrival_time', 'duration_hours', 'duration_minutes',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'base_price', 'total_seats', 'available_seats',
            'ac_available', 'sleeper_available', 'wifi_available', 'food_service'
        ]
        widgets = {
            'transport_type': forms.Select(attrs={'class': 'form-control'}),
            'operator_name': forms.TextInput(attrs={'class': 'form-control'}),
            'route_number': forms.TextInput(attrs={'class': 'form-control'}),
            'source_city': forms.TextInput(attrs={'class': 'form-control'}),
            'source_station': forms.TextInput(attrs={'class': 'form-control'}),
            'destination_city': forms.TextInput(attrs={'class': 'form-control'}),
            'destination_station': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'arrival_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
        }