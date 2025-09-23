from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime, date
import json
from .models import Hotel, HotelBooking
from .forms import HotelSearchForm, HotelBookingForm

def hotel_search_view(request):
    form = HotelSearchForm()
    hotels = []
    search_performed = False
    
    if request.GET:
        form = HotelSearchForm(request.GET)
        if form.is_valid():
            search_performed = True
            city = form.cleaned_data.get('city', '').strip()
            budget = form.cleaned_data.get('budget', '')
            min_rating = form.cleaned_data.get('min_rating')
            
            # Base query
            hotels = Hotel.objects.filter(is_active=True)
            
            # City filter
            if city:
                hotels = hotels.filter(
                    Q(city__icontains=city) |
                    Q(state__icontains=city) |
                    Q(address__icontains=city)
                )
            
            # Budget filter
            if budget:
                budget_parts = budget.split('-')
                if len(budget_parts) == 2:
                    min_price, max_price = budget_parts
                    hotels = hotels.filter(
                        price_per_night__gte=int(min_price),
                        price_per_night__lte=int(max_price)
                    )
            
            # Rating filter
            if min_rating:
                hotels = hotels.filter(overall_rating__gte=min_rating)
            
            # Amenity filters
            if form.cleaned_data.get('wifi'):
                hotels = hotels.filter(wifi=True)
            if form.cleaned_data.get('parking'):
                hotels = hotels.filter(parking=True)
            if form.cleaned_data.get('restaurant'):
                hotels = hotels.filter(restaurant=True)
            if form.cleaned_data.get('pool'):
                hotels = hotels.filter(pool=True)
    
    # Pagination
    paginator = Paginator(hotels, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'hotels': page_obj,
        'search_performed': search_performed,
        'total_results': paginator.count if search_performed else 0,
    }
    return render(request, 'hotel_booking/search.html', context)

def hotel_detail_view(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, is_active=True)
    
    # FIXED: Check both parameter names
    check_in_date = request.GET.get('check_in_date') or request.GET.get('check_in')
    check_out_date = request.GET.get('check_out_date') or request.GET.get('check_out')
    guests = request.GET.get('guests', 1)
    rooms = request.GET.get('rooms', 1)
    
    context = {
        'hotel': hotel,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'guests': guests,
        'rooms': rooms,
    }
    return render(request, 'hotel_booking/detail.html', context)

@login_required
def hotel_booking_view(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, is_active=True)
    
    # FIXED: Better parameter handling
    check_in_date = request.GET.get('check_in_date') or request.GET.get('check_in')
    check_out_date = request.GET.get('check_out_date') or request.GET.get('check_out')
    guests = int(request.GET.get('guests', 1))
    rooms = int(request.GET.get('rooms', 1))
    
    # FIXED: Better date validation
    if not check_in_date or not check_out_date:
        messages.error(request, 'Please select check-in and check-out dates from the search page.')
        return redirect('hotel_search')
    
    # Convert and validate dates
    try:
        # Handle different date formats
        for date_format in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']:
            try:
                check_in = datetime.strptime(check_in_date, date_format).date()
                check_out = datetime.strptime(check_out_date, date_format).date()
                break
            except ValueError:
                continue
        else:
            # If no format worked
            messages.error(request, 'Invalid date format. Please select dates again.')
            return redirect('hotel_search')
            
    except Exception as e:
        messages.error(request, 'Error processing dates. Please try again.')
        return redirect('hotel_search')
    
    # Validate date logic
    if check_in >= check_out:
        messages.error(request, 'Check-out date must be after check-in date.')
        return redirect('hotel_search')
    
    if check_in < date.today():
        messages.error(request, 'Check-in date cannot be in the past.')
        return redirect('hotel_search')
    
    nights = (check_out - check_in).days
    total_amount = hotel.price_per_night * nights * rooms
    
    if request.method == 'POST':
        form = HotelBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.hotel = hotel
            booking.check_in_date = check_in
            booking.check_out_date = check_out
            booking.price_per_night = hotel.price_per_night
            booking.save()
            
            # REMOVED THE PROBLEMATIC MESSAGE - No message here anymore
            
            # Create transaction and redirect to payment
            from payment_management.models import Transaction
            
            transaction = Transaction.objects.create(
                user=request.user,
                transaction_type='HOTEL_BOOKING',
                amount=booking.total_amount,
                hotel_booking=booking,
                status='PROCESSING'
            )
            
            return redirect('payment_page', transaction_id=transaction.transaction_id)
            
    else:
        # Pre-fill form with user data
        initial_data = {
            'guests': guests,
            'rooms': rooms,
            'contact_name': request.user.get_full_name(),
            'contact_phone': getattr(request.user, 'phone_number', ''),
            'contact_email': request.user.email,
        }
        form = HotelBookingForm(initial=initial_data)
    
    context = {
        'hotel': hotel,
        'form': form,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'nights': nights,
        'guests': guests,
        'rooms': rooms,
        'total_amount': total_amount,
    }
    return render(request, 'hotel_booking/booking.html', context)
# REMOVED: Old payment view - now using centralized payment system

@login_required
def booking_confirmation_view(request, booking_id):
    booking = get_object_or_404(HotelBooking, booking_id=booking_id, user=request.user)
    return render(request, 'hotel_booking/confirmation.html', {'booking': booking})

@login_required
def my_hotel_bookings_view(request):
    bookings = HotelBooking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'hotel_booking/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_hotel_booking_view(request, booking_id):
    """Cancel hotel booking"""
    booking = get_object_or_404(HotelBooking, booking_id=booking_id, user=request.user)
    
    if booking.booking_status not in ['PENDING', 'CONFIRMED']:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('my_hotel_bookings')
    
    if request.method == 'POST':
        booking.booking_status = 'CANCELLED'
        booking.save()
        
        messages.success(request, f'Booking {booking.booking_id} has been cancelled.')
        return redirect('my_hotel_bookings')
    
    context = {
        'booking': booking,
    }
    return render(request, 'hotel_booking/cancel_booking.html', context)