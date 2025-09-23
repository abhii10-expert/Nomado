from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=17, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    emergency_contact_name = forms.CharField(max_length=100, required=False)
    emergency_contact_phone = forms.CharField(max_length=17, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 
                 'date_of_birth', 'emergency_contact_name', 'emergency_contact_phone',
                 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 
                 'date_of_birth', 'emergency_contact_name', 'emergency_contact_phone')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'travel_preferences', 'preferred_budget', 
                 'notification_enabled', 'location_sharing_enabled')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'travel_preferences':
                self.fields[field].widget = forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control'})