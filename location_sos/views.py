# location_sos/views.py
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
from .email_utils import send_sos_alert_email, send_location_share_email, send_safety_checkin_email, send_alert_status_update_email

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
            email = request.POST.get('email', '').strip()
            relationship = request.POST.get('relationship', '')
            is_primary = request.POST.get('is_primary') == 'on'
            
            # Basic validation
            if not name or not email or not relationship:
                messages.error(request, 'Name, email and relationship are required.')
            else:
                # If setting as primary, remove primary status from other contacts
                if is_primary:
                    EmergencyContact.objects.filter(user=request.user, is_active=True).update(is_primary=False)
                
                # Create new contact
                EmergencyContact.objects.create(
                    user=request.user,
                    name=name,
                    email=email,
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
                contact.email = request.POST.get('email', '').strip()
                contact.relationship = request.POST.get('relationship', '')
                is_primary = request.POST.get('is_primary') == 'on'
                
                # Basic validation
                if not contact.name or not contact.email or not contact.relationship:
                    messages.error(request, 'Name, email and relationship are required.')
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
            shared_with_email = data.get('shared_with_email', '')
            
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
                shared_with_email=shared_with_email
            )
            
            # Get selected emergency contacts
            emergency_contacts = []
            if selected_contacts:
                emergency_contacts = EmergencyContact.objects.filter(
                    id__in=selected_contacts, 
                    user=request.user, 
                    is_active=True
                )
                location_share.shared_with_contacts.set(emergency_contacts)
            
            # Send email notifications
            email_count = send_location_share_email(
                location_share, 
                emergency_contacts,
                additional_email=shared_with_email if shared_with_email else None
            )
            
            # Generate sharing URL
            share_url = request.build_absolute_uri(f'/safety/shared/{location_share.share_id}/')
            
            return JsonResponse({
                'success': True,
                'message': f'Location shared successfully! {email_count} email notifications sent.',
                'share_id': str(location_share.share_id),
                'share_url': share_url,
                'expires_at': location_share.expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                'emails_sent': email_count
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
            
            # Get emergency contacts
            emergency_contacts = EmergencyContact.objects.filter(
                user=request.user, 
                is_active=True
            )
            
            # Send email notifications
            email_count = send_sos_alert_email(sos_alert, emergency_contacts)
            
            return JsonResponse({
                'success': True,
                'message': f'SOS alert sent successfully! {email_count} emergency contacts notified via email.',
                'alert_id': str(sos_alert.alert_id),
                'contacts_count': emergency_contacts.count(),
                'emails_sent': email_count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error sending SOS alert: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

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
            
            # If status is EMERGENCY or CONCERN, create SOS alert and send notifications
            email_count = 0
            if status in ['EMERGENCY', 'CONCERN']:
                # Create SOS alert for emergency/concern check-ins
                if status == 'EMERGENCY':
                    alert_type = 'EMERGENCY'
                    SOSAlert.objects.create(
                        user=request.user,
                        latitude=latitude,
                        longitude=longitude,
                        address=address,
                        alert_type=alert_type,
                        message=f"Safety check-in: {status} - {message}",
                        emails_sent=True  # Will be handled by check-in email
                    )
                
                # Send check-in email notifications
                emergency_contacts = EmergencyContact.objects.filter(
                    user=request.user, 
                    is_active=True
                )
                email_count = send_safety_checkin_email(checkin, emergency_contacts)
            
            return JsonResponse({
                'success': True,
                'message': f'Safety check-in recorded successfully! {email_count} notifications sent.' if email_count > 0 else 'Safety check-in recorded successfully!',
                'status': status,
                'created_at': checkin.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'emails_sent': email_count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error recording check-in: {str(e)}'
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
            old_status = alert.status
            alert.status = status
            if status == 'RESOLVED':
                alert.resolved_at = timezone.now()
            alert.save()
            
            # Send status update email to emergency contacts
            emergency_contacts = EmergencyContact.objects.filter(
                user=request.user, 
                is_active=True
            )
            email_count = send_alert_status_update_email(
                alert, 
                emergency_contacts, 
                updated_by=request.user
            )
            
            messages.success(request, f'SOS alert marked as {status.lower().replace("_", " ")}. {email_count} notifications sent.')
    
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
    """Test emergency contact (send test email)"""
    contact = get_object_or_404(EmergencyContact, id=contact_id, user=request.user, is_active=True)
    
    if request.method == 'POST':
        from django.core.mail import send_mail
        from django.conf import settings
        
        try:
            # Send test email
            subject = f"Test Email from {settings.DEFAULT_FROM_EMAIL.split('<')[0].strip()} Safety System"
            message = f"""Hello {contact.name},

This is a test email from the Nomado Travel Safety System.

You are registered as an emergency contact for {request.user.get_full_name() or request.user.username}.

If you receive this email, it means our emergency notification system is working correctly and you will receive alerts if {request.user.get_full_name() or request.user.username} triggers an SOS alert, shares their location, or reports a safety concern.

Please save this email address ({settings.EMAIL_HOST_USER}) to ensure our emergency notifications don't go to your spam folder.

Thank you for being a trusted emergency contact.

Best regards,
Nomado Travel Safety Team"""
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact.email],
                fail_silently=False,
            )
            
            messages.success(request, f'Test email sent successfully to {contact.name} at {contact.email}')
            
        except Exception as e:
            messages.error(request, f'Failed to send test email: {str(e)}')
        
    return redirect('emergency_contacts')