from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import json
from .models import Route, TransportBooking

class TransportSearchForm(forms.Form):
    TRANSPORT_CHOICES = [
        ('', 'All Transport Types'),
        ('FLIGHT', 'Flights'),
        ('TRAIN', 'Trains'),
        ('BUS', 'Buses'),
    ]
    
    CLASS_CHOICES = [
        ('', 'All Classes'),
        ('ECONOMY', 'Economy'),
        ('PREMIUM', 'Premium'),
        ('BUSINESS', 'Business'),
        ('FIRST', 'First Class'),
    ]
    
    # Search criteria
    source_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'From city',
            'class': 'form-control'
        })
    )
    
    destination_city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'To city',
            'class': 'form-control'
        })
    )
    
    travel_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': date.today().strftime('%Y-%m-%d')
        })
    )
    
    passengers = forms.IntegerField(
        min_value=1,
        max_value=9,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    
    # Filters
    transport_type = forms.ChoiceField(
        choices=TRANSPORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class_type = forms.ChoiceField(
        choices=CLASS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Budget filter
    BUDGET_CHOICES = [
        ('', 'Any Budget'),
        ('0-1000', 'Under ₹1,000'),
        ('1000-3000', '₹1,000 - ₹3,000'),
        ('3000-8000', '₹3,000 - ₹8,000'),
        ('8000-999999', 'Above ₹8,000'),
    ]
    
    budget = forms.ChoiceField(
        choices=BUDGET_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Departure time filter
    TIME_CHOICES = [
        ('', 'Any Time'),
        ('00:00-06:00', 'Early Morning (12 AM - 6 AM)'),
        ('06:00-12:00', 'Morning (6 AM - 12 PM)'),
        ('12:00-18:00', 'Afternoon (12 PM - 6 PM)'),
        ('18:00-23:59', 'Evening (6 PM - 12 AM)'),
    ]
    
    departure_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Amenities
    ac_required = forms.BooleanField(required=False, label="AC Required")
    wifi_required = forms.BooleanField(required=False, label="WiFi Required")
    food_service = forms.BooleanField(required=False, label="Food Service")
    
    def clean(self):
        cleaned_data = super().clean()
        travel_date = cleaned_data.get('travel_date')
        
        if travel_date and travel_date < date.today():
            raise ValidationError("Travel date cannot be in the past.")
        
        return cleaned_data

class TransportBookingForm(forms.ModelForm):
    class Meta:
        model = TransportBooking
        fields = ['passengers', 'class_type', 'contact_name', 'contact_phone', 'contact_email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class PassengerDetailsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        num_passengers = kwargs.pop('num_passengers', 1)
        super().__init__(*args, **kwargs)
        
        for i in range(num_passengers):
            self.fields[f'passenger_name_{i}'] = forms.CharField(
                max_length=100,
                label=f'Passenger {i+1} Name',
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
            self.fields[f'passenger_age_{i}'] = forms.IntegerField(
                min_value=1,
                max_value=120,
                label=f'Passenger {i+1} Age',
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )
            self.fields[f'passenger_gender_{i}'] = forms.ChoiceField(
                choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
                label=f'Passenger {i+1} Gender',
                widget=forms.Select(attrs={'class': 'form-control'})
            )
    
    def get_passenger_data(self):
        names = []
        ages = []
        genders = []
        
        i = 0
        while f'passenger_name_{i}' in self.cleaned_data:
            names.append(self.cleaned_data[f'passenger_name_{i}'])
            ages.append(self.cleaned_data[f'passenger_age_{i}'])
            genders.append(self.cleaned_data[f'passenger_gender_{i}'])
            i += 1
        
        return {
            'names': names,
            'ages': ages,
            'genders': genders
        }