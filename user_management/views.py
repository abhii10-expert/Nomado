from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from .models import UserProfile
from django.contrib.auth import get_user_model
from hotel_booking.models import Hotel, HotelBooking
from transportation.models import Route, TransportBooking
from django.core.paginator import Paginator

User = get_user_model()

def home_view(request):
    """Home page view"""
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                # Create user profile
                UserProfile.objects.create(user=user)
                username = form.cleaned_data.get('username')
                messages.success(request, f'Account created for {username}! You can now log in.')
                return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'user_management/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect based on user role
                if user.is_staff or user.is_superuser:
                    return redirect('admin_dashboard')
                
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'user_management/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# Admin check function
def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def admin_dashboard_view(request):
    """Admin dashboard with statistics and management features"""
    
    # User statistics
    total_users = User.objects.filter(is_staff=False, is_superuser=False).count()
    active_users = User.objects.filter(is_staff=False, is_superuser=False, is_active=True).count()
    new_users_this_month = User.objects.filter(
        is_staff=False,
        is_superuser=False,
        date_joined__gte=timezone.now().replace(day=1)
    ).count()
    
    # Hotel statistics
    total_hotels = Hotel.objects.count()
    active_hotels = Hotel.objects.filter(is_active=True).count()
    featured_hotels = Hotel.objects.filter(featured=True).count()
    
    # Transportation statistics
    total_routes = Route.objects.count()
    active_routes = Route.objects.filter(is_active=True).count()
    
    # Booking statistics
    total_hotel_bookings = HotelBooking.objects.count()
    pending_hotel_bookings = HotelBooking.objects.filter(booking_status='PENDING').count()
    confirmed_hotel_bookings = HotelBooking.objects.filter(booking_status='CONFIRMED').count()
    
    total_transport_bookings = TransportBooking.objects.count()
    pending_transport_bookings = TransportBooking.objects.filter(booking_status='PENDING').count()
    confirmed_transport_bookings = TransportBooking.objects.filter(booking_status='CONFIRMED').count()
    
    # Recent bookings
    recent_hotel_bookings = HotelBooking.objects.select_related('user', 'hotel').order_by('-created_at')[:5]
    recent_transport_bookings = TransportBooking.objects.select_related('user', 'route').order_by('-created_at')[:5]
    
    # Revenue (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    hotel_revenue = HotelBooking.objects.filter(
        created_at__gte=thirty_days_ago,
        booking_status__in=['CONFIRMED', 'COMPLETED']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    transport_revenue = TransportBooking.objects.filter(
        created_at__gte=thirty_days_ago,
        booking_status__in=['CONFIRMED', 'COMPLETED']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Recent users
    recent_users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')[:5]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_this_month': new_users_this_month,
        'total_hotels': total_hotels,
        'active_hotels': active_hotels,
        'featured_hotels': featured_hotels,
        'total_routes': total_routes,
        'active_routes': active_routes,
        'total_hotel_bookings': total_hotel_bookings,
        'pending_hotel_bookings': pending_hotel_bookings,
        'confirmed_hotel_bookings': confirmed_hotel_bookings,
        'total_transport_bookings': total_transport_bookings,
        'pending_transport_bookings': pending_transport_bookings,
        'confirmed_transport_bookings': confirmed_transport_bookings,
        'recent_hotel_bookings': recent_hotel_bookings,
        'recent_transport_bookings': recent_transport_bookings,
        'recent_users': recent_users,
        'hotel_revenue': hotel_revenue,
        'transport_revenue': transport_revenue,
        'total_revenue': hotel_revenue + transport_revenue,
    }
    
    return render(request, 'user_management/admin_dashboard.html', context)

@login_required
def dashboard_view(request):
    """Regular user dashboard - redirect admins to admin dashboard"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    return render(request, 'user_management/dashboard.html')

@login_required
def profile_view(request):
    """User profile - admins should not access this"""
    if request.user.is_staff or request.user.is_superuser:
        messages.warning(request, 'Admins use the admin dashboard.')
        return redirect('admin_dashboard')
    
    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'user_management/profile.html', context)

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def users_list_view(request):
    """View all users with filtering"""
    users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users_page = paginator.get_page(page)
    
    context = {
        'users': users_page,
        'total_count': users.count(),
        'search': search,
        'status': status,
    }
    return render(request, 'user_management/users_list.html', context)

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def admins_list_view(request):
    """View all admin users"""
    admins = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).order_by('-date_joined')
    
    context = {
        'admins': admins,
        'total_count': admins.count(),
    }
    return render(request, 'user_management/admins_list.html', context)

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def user_detail_view(request, user_id):
    """View detailed information about a specific user including all bookings"""
    from django.shortcuts import get_object_or_404
    
    user = get_object_or_404(User, id=user_id)
    
    # Get user's bookings
    hotel_bookings = HotelBooking.objects.filter(user=user).select_related('hotel').order_by('-created_at')
    transport_bookings = TransportBooking.objects.filter(user=user).select_related('route').order_by('-created_at')
    
    # Calculate statistics
    total_hotel_spent = hotel_bookings.filter(booking_status__in=['CONFIRMED', 'COMPLETED']).aggregate(
        total=Sum('total_amount'))['total'] or 0
    total_transport_spent = transport_bookings.filter(booking_status__in=['CONFIRMED', 'COMPLETED']).aggregate(
        total=Sum('total_amount'))['total'] or 0
    
    context = {
        'profile_user': user,
        'hotel_bookings': hotel_bookings,
        'transport_bookings': transport_bookings,
        'total_hotel_bookings': hotel_bookings.count(),
        'total_transport_bookings': transport_bookings.count(),
        'total_hotel_spent': total_hotel_spent,
        'total_transport_spent': total_transport_spent,
        'total_spent': total_hotel_spent + total_transport_spent,
    }
    return render(request, 'user_management/user_detail.html', context)

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def hotels_list_view(request):
    """View all hotels"""
    hotels = Hotel.objects.all().order_by('-created_at')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        hotels = hotels.filter(Q(name__icontains=search) | Q(city__icontains=search))
    
    # Filter
    status = request.GET.get('status', '')
    if status == 'active':
        hotels = hotels.filter(is_active=True)
    elif status == 'inactive':
        hotels = hotels.filter(is_active=False)
    elif status == 'featured':
        hotels = hotels.filter(featured=True)
    
    paginator = Paginator(hotels, 20)
    page = request.GET.get('page')
    hotels_page = paginator.get_page(page)
    
    context = {
        'hotels': hotels_page,
        'total_count': hotels.count(),
        'search': search,
        'status': status,
    }
    return render(request, 'user_management/hotels_list.html', context)

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def routes_list_view(request):
    """View all transportation routes"""
    routes = Route.objects.all().order_by('-created_at')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        routes = routes.filter(
            Q(route_number__icontains=search) |
            Q(operator_name__icontains=search) |
            Q(source_city__icontains=search) |
            Q(destination_city__icontains=search)
        )
    
    # Filter by type
    transport_type = request.GET.get('type', '')
    if transport_type:
        routes = routes.filter(transport_type=transport_type)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        routes = routes.filter(is_active=True)
    elif status == 'inactive':
        routes = routes.filter(is_active=False)
    
    paginator = Paginator(routes, 20)
    page = request.GET.get('page')
    routes_page = paginator.get_page(page)
    
    context = {
        'routes': routes_page,
        'total_count': routes.count(),
        'search': search,
        'transport_type': transport_type,
        'status': status,
    }
    return render(request, 'user_management/routes_list.html', context)

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def hotel_bookings_list_view(request):
    """View all hotel bookings"""
    bookings = HotelBooking.objects.all().select_related('user', 'hotel').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        bookings = bookings.filter(booking_status=status)
    
    # Search
    search = request.GET.get('search', '')
    if search:
        bookings = bookings.filter(
            Q(booking_id__icontains=search) |
            Q(user__username__icontains=search) |
            Q(hotel__name__icontains=search)
        )
    
    paginator = Paginator(bookings, 20)
    page = request.GET.get('page')
    bookings_page = paginator.get_page(page)
    
    context = {
        'bookings': bookings_page,
        'total_count': bookings.count(),
        'search': search,
        'status': status,
    }
    return render(request, 'user_management/hotel_bookings_list.html', context)

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def transport_bookings_list_view(request):
    """View all transport bookings"""
    bookings = TransportBooking.objects.all().select_related('user', 'route').order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        bookings = bookings.filter(booking_status=status)
    
    # Search
    search = request.GET.get('search', '')
    if search:
        bookings = bookings.filter(
            Q(booking_id__icontains=search) |
            Q(user__username__icontains=search) |
            Q(route__route_number__icontains=search)
        )
    
    paginator = Paginator(bookings, 20)
    page = request.GET.get('page')
    bookings_page = paginator.get_page(page)
    
    context = {
        'bookings': bookings_page,
        'total_count': bookings.count(),
        'search': search,
        'status': status,
    }
    return render(request, 'user_management/transport_bookings_list.html', context)

# Redirect views for main navigation
def hotel_search_view(request):
    return redirect('/hotels/search/')

def transport_search_view(request):
    return redirect('/transport/search/')

def location_share_view(request):
    return redirect('/safety/')