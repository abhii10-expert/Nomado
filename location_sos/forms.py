# location_sos/forms.py
from django import forms
from .models import EmergencyContact, LocationShare, SOSAlert, SafetyCheckIn

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'email', 'relationship', 'is_primary']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['email'].required = True
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Enter email address (required for emergency notifications)'
        })
        self.fields['is_primary'].widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})

class LocationShareForm(forms.ModelForm):
    shared_with_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional: Share with additional email address'
        })
    )
    
    class Meta:
        model = LocationShare
        fields = ['message', 'duration_hours', 'shared_with_email']
        
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional message to share with your location'
            }),
            'duration_hours': forms.Select(
                choices=[(1, '1 hour'), (2, '2 hours'), (4, '4 hours'), (8, '8 hours'), (24, '24 hours')],
                attrs={'class': 'form-control'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Add emergency contacts as checkboxes
            contacts = user.emergency_contacts.filter(is_active=True)
            for contact in contacts:
                field_name = f'contact_{contact.id}'
                self.fields[field_name] = forms.BooleanField(
                    required=False,
                    label=f'{contact.name} ({contact.get_relationship_display()}) - {contact.email}',
                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                )

class SOSAlertForm(forms.ModelForm):
    class Meta:
        model = SOSAlert
        fields = ['alert_type', 'message']
        
        widgets = {
            'alert_type': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your emergency situation...'
            }),
        }

class SafetyCheckInForm(forms.ModelForm):
    class Meta:
        model = SafetyCheckIn
        fields = ['status', 'message']
        
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional message about your status'
            }),
        }

class QuickSOSForm(forms.Form):
    """Simple form for quick SOS trigger"""
    alert_type = forms.ChoiceField(
        choices=SOSAlert.ALERT_TYPE,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Brief description of emergency (optional)'
        })
    )