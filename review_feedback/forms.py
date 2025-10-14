from django import forms
from .models import HotelReview, TransportReview, Feedback

class HotelReviewForm(forms.ModelForm):
    class Meta:
        model = HotelReview
        fields = [
            'overall_rating', 'cleanliness_rating', 'comfort_rating', 
            'service_rating', 'value_rating', 'location_rating',
            'title', 'review_text', 'room_type'
        ]
        widgets = {
            'overall_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'cleanliness_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comfort_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'service_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'value_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'location_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Summary of your stay'}),
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Share your experience...'}),
            'room_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Deluxe Room'}),
        }

class TransportReviewForm(forms.ModelForm):
    class Meta:
        model = TransportReview
        fields = [
            'overall_rating', 'punctuality_rating', 'comfort_rating',
            'service_rating', 'value_rating', 'title', 'review_text'
        ]
        widgets = {
            'overall_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'punctuality_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comfort_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'service_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'value_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Summary of your journey'}),
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Share your experience...'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'subject', 'message', 'email', 'phone']
        widgets = {
            'feedback_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }