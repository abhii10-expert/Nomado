from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .models import ServiceProvider, ProviderEarnings
from .forms import HotelForm, HotelImageForm, RouteForm
from hotel_booking.models import Hotel, HotelBooking, HotelImage
from transportation.models import Route, TransportBooking

def is_service_provider(user):
    return user.is_authenticated and user.is_service_provider and hasattr(user, 'serviceprovider')

@login_required
def provider_dashboard_view(request):
    if not is_service_provider(request.user):
        messages.error(request, 'You need to be a verified service provider to access this page.')
        return redirect('home')
    
    provider = request.user.serviceprovider
    
    # Get statistics
    if provider.provider_type in ['HOTEL', 'BOTH']:
        hotels = Hotel.objects.filter(owner=provider)
        hotel_count = hotels.count()
        hotel_bookings = HotelBooking.objects.filter(hotel__owner=provider)
        hotel_bookings_count = hotel_bookings.count()
        hotel_revenue = hotel_bookings.filter(booking_status__in=['CONFIRMED', 'COMPLETED']).aggregate(
            total=Sum('total_amount'))['total'] or 0
    else:
        hotel_count = 0
        hotel_bookings_count = 0
        hotel_revenue = 0
    
    if provider.provider_type in ['TRANSPORT', 'BOTH']:
        routes = Route.objects.filter(owner=provider)
        routes_count = routes.count()
        transport_bookings = TransportBooking.objects.filter(route__owner=provider)
        transport_bookings_count = transport_bookings.count()
        transport_revenue = transport_bookings.filter(booking_status__in=['CONFIRMED', 'COMPLETED']).aggregate(
            total=Sum('total_amount'))['total'] or 0
    else:
        routes_count = 0
        transport_bookings_count = 0
        transport_revenue = 0
    
    context = {
        'provider': provider,
        'hotel_count': hotel_count,
        'hotel_bookings_count': hotel_bookings_count,
        'hotel_revenue': hotel_revenue,
        'routes_count': routes_count,
        'transport_bookings_count': transport_bookings_count,
        'transport_revenue': transport_revenue,
        'total_revenue': hotel_revenue + transport_revenue,
    }
    return render(request, 'service_provider/dashboard.html', context)

@login_required
def provider_hotels_view(request):
    if not is_service_provider(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    provider = request.user.serviceprovider
    
    if provider.provider_type not in ['HOTEL', 'BOTH']:
        messages.error(request, 'Your account is not authorized to manage hotels.')
        return redirect('provider_dashboard')
    
    hotels = Hotel.objects.filter(owner=provider)
    
    context = {
        'provider': provider,
        'hotels': hotels,
    }
    return render(request, 'service_provider/hotels.html', context)

@login_required
def provider_add_hotel_view(request):
    if not is_service_provider(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    provider = request.user.serviceprovider
    
    if provider.provider_type not in ['HOTEL', 'BOTH']:
        messages.error(request, 'Your account is not authorized to manage hotels.')
        return redirect('provider_dashboard')
    
    if request.method == 'POST':
        form = HotelForm(request.POST)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.owner = provider
            hotel.is_active = False  # Needs admin approval
            hotel.save()
            messages.success(request, 'Hotel added successfully! Awaiting admin approval.')
            return redirect('provider_hotels')
    else:
        form = HotelForm()
    
    return render(request, 'service_provider/add_hotel.html', {'form': form, 'provider': provider})

@login_required
def provider_edit_hotel_view(request, hotel_id):
    if not is_service_provider(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    provider = request.user.serviceprovider
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=provider)
    
    if request.method == 'POST':
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hotel updated successfully!')
            return redirect('provider_hotels')
    else:
        form = HotelForm(instance=hotel)
    
    return render(request, 'service_provider/edit_hotel.html', {'form': form, 'hotel': hotel, 'provider': provider})

@login_required
def provider_transport_view(request):
    if not is_service_provider(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    provider = request.user.serviceprovider
    
    if provider.provider_type not in ['TRANSPORT', 'BOTH']:
        messages.error(request, 'Your account is not authorized to manage transport.')
        return redirect('provider_dashboard')
    
    routes = Route.objects.filter(owner=provider)
    
    context = {
        'provider': provider,
        'routes': routes,
    }
    return render(request, 'service_provider/transport.html', context)

@login_required
def provider_add_route_view(request):
    if not is_service_provider(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    provider = request.user.serviceprovider
    
    if provider.provider_type not in ['TRANSPORT', 'BOTH']:
        messages.error(request, 'Your account is not authorized to manage transport.')
        return redirect('provider_dashboard')
    
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.owner = provider
            route.is_active = False  # Needs admin approval
            route.save()
            messages.success(request, 'Route added successfully! Awaiting admin approval.')
            return redirect('provider_transport')
    else:
        form = RouteForm()
    
    return render(request, 'service_provider/add_route.html', {'form': form, 'provider': provider})

@login_required
def provider_edit_route_view(request, route_id):
    if not is_service_provider(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    provider = request.user.serviceprovider
    route = get_object_or_404(Route, id=route_id, owner=provider)
    
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route updated successfully!')
            return redirect('provider_transport')
    else:
        form = RouteForm(instance=route)
    
    return render(request, 'service_provider/edit_route.html', {'form': form, 'route': route, 'provider': provider})

@login_required
def provider_bookings_view(request):
    if not is_service_provider(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    provider = request.user.serviceprovider
    
    hotel_bookings = HotelBooking.objects.filter(hotel__owner=provider).select_related('hotel', 'user').order_by('-created_at')
    transport_bookings = TransportBooking.objects.filter(route__owner=provider).select_related('route', 'user').order_by('-created_at')
    
    context = {
        'provider': provider,
        'hotel_bookings': hotel_bookings,
        'transport_bookings': transport_bookings,
    }
    return render(request, 'service_provider/bookings.html', context)

@login_required
def provider_earnings_view(request):
    if not is_service_provider(request.user):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    provider = request.user.serviceprovider
    earnings = ProviderEarnings.objects.filter(provider=provider).order_by('-created_at')
    
    total_earnings = earnings.aggregate(total=Sum('provider_earnings'))['total'] or 0
    settled_earnings = earnings.filter(is_settled=True).aggregate(total=Sum('provider_earnings'))['total'] or 0
    pending_earnings = total_earnings - settled_earnings
    
    context = {
        'provider': provider,
        'earnings': earnings,
        'total_earnings': total_earnings,
        'settled_earnings': settled_earnings,
        'pending_earnings': pending_earnings,
    }
    return render(request, 'service_provider/earnings.html', context)

def provider_register_view(request):
    messages.info(request, 'Service provider registration is managed by administrators. Please contact support.')
    return redirect('home')