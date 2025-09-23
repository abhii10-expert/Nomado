from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from .models import UserProfile

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

@login_required
def dashboard_view(request):
    return render(request, 'user_management/dashboard.html')

@login_required
def profile_view(request):
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

# Redirect views for main navigation
def hotel_search_view(request):
    return redirect('/hotels/search/')

def transport_search_view(request):
    return redirect('/transport/search/')

def location_share_view(request):
    return redirect('/safety/')