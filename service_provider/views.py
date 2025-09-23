from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def provider_dashboard_view(request):
    return render(request, 'service_provider/dashboard.html')

def provider_register_view(request):
    return render(request, 'service_provider/register.html')

@login_required
def provider_hotels_view(request):
    return render(request, 'service_provider/hotels.html')

@login_required
def provider_transport_view(request):
    return render(request, 'service_provider/transport.html')

@login_required
def provider_bookings_view(request):
    return render(request, 'service_provider/bookings.html')

@login_required
def provider_earnings_view(request):
    return render(request, 'service_provider/earnings.html')