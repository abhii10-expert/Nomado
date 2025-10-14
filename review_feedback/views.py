from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HotelReview, TransportReview, Feedback
from .forms import HotelReviewForm, TransportReviewForm, FeedbackForm
from hotel_booking.models import Hotel, HotelBooking
from transportation.models import Route, TransportBooking

@login_required
def hotel_review_view(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    # Check if user has completed booking for this hotel
    has_booking = HotelBooking.objects.filter(
        user=request.user,
        hotel=hotel,
        booking_status='COMPLETED'
    ).exists()
    
    # Check if already reviewed
    existing_review = HotelReview.objects.filter(user=request.user, hotel=hotel).first()
    
    if request.method == 'POST':
        if not has_booking:
            messages.error(request, 'You can only review hotels you have stayed at.')
            return redirect('hotel_detail', hotel_id=hotel.id)
        
        if existing_review:
            form = HotelReviewForm(request.POST, instance=existing_review)
            action = 'updated'
        else:
            form = HotelReviewForm(request.POST)
            action = 'submitted'
        
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.hotel = hotel
            review.is_verified = True  # Verified because they have booking
            
            # Get the booking
            booking = HotelBooking.objects.filter(
                user=request.user,
                hotel=hotel,
                booking_status='COMPLETED'
            ).first()
            review.booking = booking
            review.stayed_date = booking.check_out_date if booking else None
            
            review.save()
            messages.success(request, f'Your review has been {action} successfully!')
            return redirect('hotel_detail', hotel_id=hotel.id)
    else:
        form = HotelReviewForm(instance=existing_review) if existing_review else HotelReviewForm()
    
    context = {
        'hotel': hotel,
        'form': form,
        'has_booking': has_booking,
        'existing_review': existing_review,
    }
    return render(request, 'review_feedback/hotel_review.html', context)

@login_required
def transport_review_view(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    
    # Check if user has completed booking for this route
    has_booking = TransportBooking.objects.filter(
        user=request.user,
        route=route,
        booking_status='COMPLETED'
    ).exists()
    
    # Check if already reviewed
    existing_review = TransportReview.objects.filter(user=request.user, route=route).first()
    
    if request.method == 'POST':
        if not has_booking:
            messages.error(request, 'You can only review routes you have traveled on.')
            return redirect('transport_search')
        
        if existing_review:
            form = TransportReviewForm(request.POST, instance=existing_review)
            action = 'updated'
        else:
            form = TransportReviewForm(request.POST)
            action = 'submitted'
        
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.route = route
            review.is_verified = True
            
            # Get the booking
            booking = TransportBooking.objects.filter(
                user=request.user,
                route=route,
                booking_status='COMPLETED'
            ).first()
            review.booking = booking
            review.travel_date = booking.travel_date if booking else None
            
            review.save()
            messages.success(request, f'Your review has been {action} successfully!')
            return redirect('transport_search')
    else:
        form = TransportReviewForm(instance=existing_review) if existing_review else TransportReviewForm()
    
    context = {
        'route': route,
        'form': form,
        'has_booking': has_booking,
        'existing_review': existing_review,
    }
    return render(request, 'review_feedback/transport_review.html', context)

@login_required
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('home')
    else:
        initial_data = {
            'email': request.user.email,
            'phone': getattr(request.user, 'phone_number', ''),
        }
        form = FeedbackForm(initial=initial_data)
    
    return render(request, 'review_feedback/feedback.html', {'form': form})

@login_required
def reviews_dashboard_view(request):
    hotel_reviews = HotelReview.objects.filter(user=request.user)
    transport_reviews = TransportReview.objects.filter(user=request.user)
    
    context = {
        'hotel_reviews': hotel_reviews,
        'transport_reviews': transport_reviews,
    }
    return render(request, 'review_feedback/dashboard.html', context)