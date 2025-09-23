from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import HotelBooking

class HotelSearchForm(forms.Form):
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter city name',
            'class': 'form-control'
        })
    )
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': date.today().strftime('%Y-%m-%d')
        })
    )
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        })
    )
    guests = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    rooms = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control'
        })
    )
    
    # Filters
    BUDGET_CHOICES = [
        ('', 'Any Budget'),
        ('0-2000', 'Under ₹2,000'),
        ('2000-5000', '₹2,000 - ₹5,000'),
        ('5000-10000', '₹5,000 - ₹10,000'),
        ('10000-999999', 'Above ₹10,000'),
    ]
    
    budget = forms.ChoiceField(
        choices=BUDGET_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_rating = forms.FloatField(
        min_value=0,
        max_value=5,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'Minimum rating'
        })
    )
    
    # Amenities
    wifi = forms.BooleanField(required=False, label="WiFi")
    parking = forms.BooleanField(required=False, label="Parking")
    restaurant = forms.BooleanField(required=False, label="Restaurant")
    pool = forms.BooleanField(required=False, label="Swimming Pool")
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            if check_in >= check_out:
                raise ValidationError("Check-out date must be after check-in date.")
            
            if check_in < date.today():
                raise ValidationError("Check-in date cannot be in the past.")
        
        return cleaned_data

class HotelBookingForm(forms.ModelForm):
    class Meta:
        model = HotelBooking
        fields = ['guests', 'rooms', 'special_requests', 'contact_name', 'contact_phone', 'contact_email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['special_requests'].widget = forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Any special requests or requirements...',
            'class': 'form-control'
        })