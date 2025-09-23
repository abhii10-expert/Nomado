from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime, time, date
import json
from .models import Route, TransportBooking
from .forms import TransportSearchForm, TransportBookingForm, PassengerDetailsForm

def transport_search_view(request):
    form = TransportSearchForm()
    routes = []
    search_performed = False
    
    if request.GET:
        form = TransportSearchForm(request.GET)
        if form.is_valid():
            search_performed = True
            
            # Get form data
            source_city = form.cleaned_data.get('source_city', '').strip()
            destination_city = form.cleaned_data.get('destination_city', '').strip()
            travel_date = form.cleaned_data.get('travel_date')
            passengers = form.cleaned_data.get('passengers', 1)
            transport_type = form.cleaned_data.get('transport_type', '')
            budget = form.cleaned_data.get('budget', '')
            departure_time = form.cleaned_data.get('departure_time', '')
            
            # Base query
            routes = Route.objects.filter(is_active=True)
            
            # City filters
            if source_city:
                routes = routes.filter(source_city__icontains=source_city)
            if destination_city:
                routes = routes.filter(destination_city__icontains=destination_city)
                
            # Transport type filter
            if transport_type:
                routes = routes.filter(transport_type=transport_type)
            
            # Availability filter
            routes = routes.filter(available_seats__gte=passengers)
            
            # Budget filter
            if budget:
                budget_parts = budget.split('-')
                if len(budget_parts) == 2:
                    min_price, max_price = budget_parts
                    routes = routes.filter(
                        base_price__gte=int(min_price),
                        base_price__lte=int(max_price)
                    )
            
            # Departure time filter
            if departure_time:
                time_parts = departure_time.split('-')
                if len(time_parts) == 2:
                    start_time = datetime.strptime(time_parts[0], '%H:%M').time()
                    end_time = datetime.strptime(time_parts[1], '%H:%M').time()
                    routes = routes.filter(
                        departure_time__gte=start_time,
                        departure_time__lte=end_time
                    )
            
            # Amenity filters
            if form.cleaned_data.get('ac_required'):
                routes = routes.filter(ac_available=True)
            if form.cleaned_data.get('wifi_required'):
                routes = routes.filter(wifi_available=True)
            if form.cleaned_data.get('food_service'):
                routes = routes.filter(food_service=True)
            
            # Day of week filter based on travel date
            if travel_date:
                day_of_week = travel_date.weekday()  # 0=Monday, 6=Sunday
                day_fields = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                filter_dict = {day_fields[day_of_week]: True}
                routes = routes.filter(**filter_dict)
    
    # Pagination
    paginator = Paginator(routes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'routes': page_obj,
        'search_performed': search_performed,
        'total_results': paginator.count if search_performed else 0,
    }
    return render(request, 'transportation/search.html', context)

def route_detail_view(request, route_id):
    route = get_object_or_404(Route, id=route_id, is_active=True)
    
    # Get search parameters
    travel_date = request.GET.get('travel_date')
    passengers = int(request.GET.get('passengers', 1))
    
    context = {
        'route': route,
        'travel_date': travel_date,
        'passengers': passengers,
    }
    return render(request, 'transportation/detail.html', context)

@login_required
def transport_booking_view(request, route_id):
    route = get_object_or_404(Route, id=route_id, is_active=True)
    
    # FIXED: Better parameter handling
    travel_date = request.GET.get('travel_date')
    passengers = int(request.GET.get('passengers', 1))
    
    # FIXED: Better date validation
    if not travel_date or travel_date == 'None':
        messages.error(request, 'Please select a travel date from the search page.')
        return redirect('transport_search')
    
    # Validate and parse travel date
    try:
        # Handle different date formats
        for date_format in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']:
            try:
                travel_date_obj = datetime.strptime(travel_date, date_format).date()
                break
            except ValueError:
                continue
        else:
            # If no format worked
            messages.error(request, 'Invalid travel date format. Please select date again.')
            return redirect('transport_search')
            
        # Validate date logic
        if travel_date_obj < date.today():
            messages.error(request, 'Travel date cannot be in the past.')
            return redirect('transport_search')
            
    except Exception as e:
        messages.error(request, 'Error processing travel date. Please try again.')
        return redirect('transport_search')
    
    # Check availability
    if route.available_seats < passengers:
        messages.error(request, f'Only {route.available_seats} seats available. You requested {passengers} seats.')
        return redirect('route_detail', route_id=route.id)
    
    if request.method == 'POST':
        booking_form = TransportBookingForm(request.POST)
        passenger_form = PassengerDetailsForm(request.POST, num_passengers=passengers)
        
        if booking_form.is_valid() and passenger_form.is_valid():
            # Create booking
            booking = booking_form.save(commit=False)
            booking.user = request.user
            booking.route = route
            booking.travel_date = travel_date_obj
            booking.price_per_ticket = route.base_price
            
            # Get passenger details
            passenger_data = passenger_form.get_passenger_data()
            booking.passenger_names = json.dumps(passenger_data['names'])
            booking.passenger_ages = json.dumps(passenger_data['ages'])
            booking.passenger_genders = json.dumps(passenger_data['genders'])
            
            booking.save()
            
            # REMOVED THE PROBLEMATIC MESSAGE - No message here anymore
            
            # Create transaction and redirect to payment
            from payment_management.models import Transaction
            
            transaction = Transaction.objects.create(
                user=request.user,
                transaction_type='TRANSPORT_BOOKING',
                amount=booking.total_amount,
                transport_booking=booking,
                status='PROCESSING'
            )
            
            return redirect('payment_page', transaction_id=transaction.transaction_id)
            
    else:
        # Pre-fill forms
        initial_booking_data = {
            'passengers': passengers,
            'contact_name': request.user.get_full_name(),
            'contact_phone': getattr(request.user, 'phone_number', ''),
            'contact_email': request.user.email,
        }
        booking_form = TransportBookingForm(initial=initial_booking_data)
        passenger_form = PassengerDetailsForm(num_passengers=passengers)
    
    # Calculate total
    total_amount = route.base_price * passengers
    
    context = {
        'route': route,
        'booking_form': booking_form,
        'passenger_form': passenger_form,
        'travel_date': travel_date,
        'passengers': passengers,
        'total_amount': total_amount,
    }
    return render(request, 'transportation/booking.html', context)
# REMOVED: Old payment views - now using centralized payment system

@login_required
def transport_booking_confirmation_view(request, booking_id):
    booking = get_object_or_404(TransportBooking, booking_id=booking_id, user=request.user)
    
    # Parse passenger details
    passenger_names = json.loads(booking.passenger_names)
    passenger_ages = json.loads(booking.passenger_ages)
    passenger_genders = json.loads(booking.passenger_genders)
    
    passengers = []
    for i in range(len(passenger_names)):
        passengers.append({
            'name': passenger_names[i],
            'age': passenger_ages[i],
            'gender': passenger_genders[i]
        })
    
    context = {
        'booking': booking,
        'passengers': passengers,
    }
    return render(request, 'transportation/confirmation.html', context)

@login_required
def my_transport_bookings_view(request):
    bookings = TransportBooking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'transportation/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_transport_booking_view(request, booking_id):
    """Cancel transport booking"""
    booking = get_object_or_404(TransportBooking, booking_id=booking_id, user=request.user)
    
    if booking.booking_status not in ['PENDING', 'CONFIRMED']:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('my_transport_bookings')
    
    if request.method == 'POST':
        # Restore seats if booking was confirmed
        if booking.booking_status == 'CONFIRMED':
            route = booking.route
            route.available_seats += booking.passengers
            route.save()
        
        booking.booking_status = 'CANCELLED'
        booking.save()
        
        messages.success(request, f'Booking {booking.booking_id} has been cancelled.')
        return redirect('my_transport_bookings')
    
    context = {
        'booking': booking,
    }
    return render(request, 'transportation/cancel_booking.html', context)