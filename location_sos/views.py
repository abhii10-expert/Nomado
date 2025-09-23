from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
import json
from .models import EmergencyContact, LocationShare, SOSAlert, SafetyCheckIn
from .forms import EmergencyContactForm, LocationShareForm, SOSAlertForm, SafetyCheckInForm, QuickSOSForm

@login_required
def location_dashboard_view(request):
    """Main dashboard for location and safety features"""
    # Get recent activity
    recent_shares = LocationShare.objects.filter(user=request.user)[:5]
    recent_alerts = SOSAlert.objects.filter(user=request.user)[:5]
    recent_checkins = SafetyCheckIn.objects.filter(user=request.user)[:5]
    
    # Get emergency contacts
    emergency_contacts = EmergencyContact.objects.filter(user=request.user, is_active=True)
    
    # Get active location shares
    active_shares = LocationShare.objects.filter(
        user=request.user, 
        status='ACTIVE',
        expires_at__gt=timezone.now()
    )
    
    context = {
        'emergency_contacts': emergency_contacts,
        'recent_shares': recent_shares,
        'recent_alerts': recent_alerts,
        'recent_checkins': recent_checkins,
        'active_shares': active_shares,
    }
    return render(request, 'location_sos/dashboard.html', context)

@login_required
def emergency_contacts_view(request):
    """Manage emergency contacts"""
    contacts = EmergencyContact.objects.filter(user=request.user, is_active=True)
    editing = None
    
    # Handle GET request for editing
    edit_id = request.GET.get('edit')
    if edit_id:
        try:
            editing = EmergencyContact.objects.get(id=edit_id, user=request.user, is_active=True)
        except EmergencyContact.DoesNotExist:
            messages.error(request, 'Contact not found.')
            return redirect('emergency_contacts')
    
    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete':
            # Delete contact
            contact_id = request.POST.get('contact_id')
            try:
                contact = EmergencyContact.objects.get(id=contact_id, user=request.user, is_active=True)
                contact.is_active = False
                contact.save()
                messages.success(request, f'Emergency contact "{contact.name}" removed successfully!')
            except EmergencyContact.DoesNotExist:
                messages.error(request, 'Contact not found.')
            return redirect('emergency_contacts')
            
        elif action == 'add':
            # Add new contact
            name = request.POST.get('name', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            email = request.POST.get('email', '').strip()
            relationship = request.POST.get('relationship', '')
            is_primary = request.POST.get('is_primary') == 'on'
            
            # Basic validation
            if not name or not phone_number or not relationship:
                messages.error(request, 'Name, phone number, and relationship are required.')
            else:
                # If setting as primary, remove primary status from other contacts
                if is_primary:
                    EmergencyContact.objects.filter(user=request.user, is_active=True).update(is_primary=False)
                
                # Create new contact
                EmergencyContact.objects.create(
                    user=request.user,
                    name=name,
                    phone_number=phone_number,
                    email=email if email else None,
                    relationship=relationship,
                    is_primary=is_primary
                )
                messages.success(request, f'Emergency contact "{name}" added successfully!')
            return redirect('emergency_contacts')
            
        elif action == 'edit':
            # Edit existing contact
            contact_id = request.POST.get('contact_id')
            try:
                contact = EmergencyContact.objects.get(id=contact_id, user=request.user, is_active=True)
                
                contact.name = request.POST.get('name', '').strip()
                contact.phone_number = request.POST.get('phone_number', '').strip()
                contact.email = request.POST.get('email', '').strip() or None
                contact.relationship = request.POST.get('relationship', '')
                is_primary = request.POST.get('is_primary') == 'on'
                
                # Basic validation
                if not contact.name or not contact.phone_number or not contact.relationship:
                    messages.error(request, 'Name, phone number, and relationship are required.')
                else:
                    # If setting as primary, remove primary status from other contacts
                    if is_primary and not contact.is_primary:
                        EmergencyContact.objects.filter(user=request.user, is_active=True).exclude(id=contact.id).update(is_primary=False)
                    
                    contact.is_primary = is_primary
                    contact.save()
                    messages.success(request, f'Emergency contact "{contact.name}" updated successfully!')
                    return redirect('emergency_contacts')
                    
            except EmergencyContact.DoesNotExist:
                messages.error(request, 'Contact not found.')
                return redirect('emergency_contacts')
    
    context = {
        'contacts': contacts,
        'editing': editing,
    }
    return render(request, 'location_sos/emergency_contacts.html', context)

@login_required
def edit_emergency_contact_view(request, contact_id):
    """Edit emergency contact"""
    contact = get_object_or_404(EmergencyContact, id=contact_id, user=request.user)
    
    if request.method == 'POST':
        form = EmergencyContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Emergency contact updated successfully!')
            return redirect('emergency_contacts')
    else:
        form = EmergencyContactForm(instance=contact)
    
    context = {
        'form': form,
        'contact': contact,
        'editing': True,
    }
    return render(request, 'location_sos/emergency_contacts.html', context)

@login_required
def delete_emergency_contact_view(request, contact_id):
    """Delete emergency contact"""
    contact = get_object_or_404(EmergencyContact, id=contact_id, user=request.user)
    
    if request.method == 'POST':
        contact.is_active = False
        contact.save()
        messages.success(request, 'Emergency contact removed successfully!')
    
    return redirect('emergency_contacts')

@login_required
def location_share_view(request):
    """Share current location"""
    emergency_contacts = EmergencyContact.objects.filter(user=request.user, is_active=True)
    
    if request.method == 'POST':
        form = LocationShareForm(request.POST, user=request.user)
        if form.is_valid():
            # This will be handled via AJAX with location data
            messages.info(request, 'Please allow location access to share your location.')
            return render(request, 'location_sos/share_location.html', {
                'form': form,
                'contacts': emergency_contacts
            })
    else:
        form = LocationShareForm(user=request.user)
    
    context = {
        'form': form,
        'contacts': emergency_contacts,
    }
    return render(request, 'location_sos/share_location.html', context)

@csrf_exempt
@login_required
def share_location_ajax(request):
    """Handle location sharing via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
            address = data.get('address', '')
            message = data.get('message', '')
            duration_hours = int(data.get('duration_hours', 1))
            selected_contacts = data.get('selected_contacts', [])
            shared_with_phone = data.get('shared_with_phone', '')
            
            # Create location share
            expires_at = timezone.now() + timedelta(hours=duration_hours)
            
            location_share = LocationShare.objects.create(
                user=request.user,
                latitude=latitude,
                longitude=longitude,
                address=address,
                message=message,
                duration_hours=duration_hours,
                expires_at=expires_at,
                shared_with_phone=shared_with_phone
            )
            
            # Add selected emergency contacts
            if selected_contacts:
                contacts = EmergencyContact.objects.filter(
                    id__in=selected_contacts, 
                    user=request.user, 
                    is_active=True
                )
                location_share.shared_with_contacts.set(contacts)
            
            # Generate sharing URL
            share_url = request.build_absolute_uri(f'/safety/shared/{location_share.share_id}/')
            
            return JsonResponse({
                'success': True,
                'message': 'Location shared successfully!',
                'share_id': str(location_share.share_id),
                'share_url': share_url,
                'expires_at': location_share.expires_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error sharing location: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
@login_required
def trigger_sos_ajax(request):
    """Handle SOS alert via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
            address = data.get('address', '')
            alert_type = data.get('alert_type', 'EMERGENCY')
            message = data.get('message', '')
            
            # Create SOS alert
            sos_alert = SOSAlert.objects.create(
                user=request.user,
                latitude=latitude,
                longitude=longitude,
                address=address,
                alert_type=alert_type,
                message=message
            )
            
            # In a real application, you would send notifications here
            # For now, we'll just mark as contacts notified
            sos_alert.contacts_notified = True
            sos_alert.save()
            
            # Get emergency contacts for notification simulation
            emergency_contacts = EmergencyContact.objects.filter(
                user=request.user, 
                is_active=True
            )
            
            # Create notification message
            notification_message = f"SOS ALERT from {request.user.get_full_name() or request.user.username}"
            if message:
                notification_message += f": {message}"
            notification_message += f"\nLocation: {address or f'{latitude}, {longitude}'}"
            notification_message += f"\nTime: {sos_alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            
            return JsonResponse({
                'success': True,
                'message': 'SOS alert sent successfully!',
                'alert_id': str(sos_alert.alert_id),
                'contacts_count': emergency_contacts.count(),
                'notification_message': notification_message
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error sending SOS alert: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def sos_alerts_view(request):
    """View SOS alerts history"""
    alerts = SOSAlert.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(alerts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'alerts': page_obj,
        'total_alerts': alerts.count(),
    }
    return render(request, 'location_sos/sos_alerts.html', context)

@login_required
def update_sos_status_view(request, alert_id):
    """Update SOS alert status"""
    alert = get_object_or_404(SOSAlert, alert_id=alert_id, user=request.user)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['RESOLVED', 'FALSE_ALARM']:
            alert.status = status
            if status == 'RESOLVED':
                alert.resolved_at = timezone.now()
            alert.save()
            messages.success(request, f'SOS alert marked as {status.lower().replace("_", " ")}.')
    
    return redirect('sos_alerts')

@login_required
def safety_checkin_view(request):
    """Safety check-in"""
    if request.method == 'POST':
        form = SafetyCheckInForm(request.POST)
        if form.is_valid():
            # Handle via AJAX for location
            return redirect('safety_checkin_confirm')
    else:
        form = SafetyCheckInForm()
    
    recent_checkins = SafetyCheckIn.objects.filter(user=request.user)[:10]
    context = {
        'form': form,
        'recent_checkins': recent_checkins,
    }
    return render(request, 'location_sos/safety_checkin.html', context)

@csrf_exempt
@login_required
def safety_checkin_ajax(request):
    """Handle safety check-in via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
            address = data.get('address', '')
            status = data.get('status', 'SAFE')
            message = data.get('message', '')
            
            # Create safety check-in
            checkin = SafetyCheckIn.objects.create(
                user=request.user,
                latitude=latitude,
                longitude=longitude,
                address=address,
                status=status,
                message=message
            )
            
            # If status is EMERGENCY or CONCERN, create SOS alert
            if status in ['EMERGENCY', 'CONCERN']:
                alert_type = 'EMERGENCY' if status == 'EMERGENCY' else 'OTHER'
                SOSAlert.objects.create(
                    user=request.user,
                    latitude=latitude,
                    longitude=longitude,
                    address=address,
                    alert_type=alert_type,
                    message=f"Safety check-in: {status} - {message}",
                    contacts_notified=True
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Safety check-in recorded successfully!',
                'status': status,
                'created_at': checkin.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error recording check-in: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def view_shared_location(request, share_id):
    """Public view for shared location"""
    try:
        location_share = get_object_or_404(LocationShare, share_id=share_id)
        
        # Check if location sharing has expired
        if location_share.expires_at < timezone.now():
            location_share.status = 'EXPIRED'
            location_share.save()
            context = {
                'expired': True,
                'user_name': location_share.user.get_full_name() or location_share.user.username
            }
            return render(request, 'location_sos/view_shared_location.html', context)
        
        # Update last accessed time
        location_share.last_updated = timezone.now()
        location_share.save()
        
        context = {
            'location_share': location_share,
            'user_name': location_share.user.get_full_name() or location_share.user.username,
            'time_remaining': (location_share.expires_at - timezone.now()).total_seconds() / 3600,  # hours
        }
        return render(request, 'location_sos/view_shared_location.html', context)
        
    except LocationShare.DoesNotExist:
        context = {
            'not_found': True
        }
        return render(request, 'location_sos/view_shared_location.html', context)

@login_required
def my_location_shares_view(request):
    """View user's location sharing history"""
    shares = LocationShare.objects.filter(user=request.user)
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        shares = shares.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(shares, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'shares': page_obj,
        'total_shares': shares.count(),
        'status_filter': status_filter,
    }
    return render(request, 'location_sos/my_shares.html', context)

@login_required
def stop_location_share_view(request, share_id):
    """Stop an active location share"""
    location_share = get_object_or_404(
        LocationShare, 
        share_id=share_id, 
        user=request.user, 
        status='ACTIVE'
    )
    
    if request.method == 'POST':
        location_share.status = 'STOPPED'
        location_share.save()
        messages.success(request, 'Location sharing stopped successfully!')
    
    return redirect('location_dashboard')

@login_required
def safety_checkin_history_view(request):
    """View safety check-in history"""
    checkins = SafetyCheckIn.objects.filter(user=request.user)
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        checkins = checkins.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(checkins, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'checkins': page_obj,
        'total_checkins': checkins.count(),
        'status_filter': status_filter,
    }
    return render(request, 'location_sos/checkin_history.html', context)

@login_required
def emergency_contact_test_view(request, contact_id):
    """Test emergency contact (send test message)"""
    contact = get_object_or_404(EmergencyContact, id=contact_id, user=request.user, is_active=True)
    
    if request.method == 'POST':
        # In a real application, you would send an actual SMS/call here
        # For now, we'll just simulate it
        test_message = f"This is a test message from Nomado Safety System for {request.user.get_full_name() or request.user.username}. Your contact information is working correctly."
        
        messages.success(request, f'Test message sent to {contact.name} at {contact.phone_number}')
        
        # Log the test (you could create a model for this)
        
    return redirect('emergency_contacts')

# Admin views for managing alerts (if needed)
@login_required
def admin_sos_alerts_view(request):
    """Admin view for all SOS alerts (for staff only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('location_dashboard')
    
    alerts = SOSAlert.objects.all().select_related('user')
    
    # Filter options
    status_filter = request.GET.get('status')
    if status_filter:
        alerts = alerts.filter(status=status_filter)
    
    type_filter = request.GET.get('type')
    if type_filter:
        alerts = alerts.filter(alert_type=type_filter)
    
    # Pagination
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'alerts': page_obj,
        'total_alerts': alerts.count(),
        'status_filter': status_filter,
        'type_filter': type_filter,
        'alert_types': SOSAlert.ALERT_TYPE,
        'alert_statuses': SOSAlert.ALERT_STATUS,
    }
    return render(request, 'location_sos/admin_alerts.html', context)