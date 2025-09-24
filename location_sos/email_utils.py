# location_sos/email_utils.py
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

def send_sos_alert_email(sos_alert, emergency_contacts):
    """Send SOS alert email to emergency contacts"""
    try:
        user = sos_alert.user
        user_name = user.get_full_name() or user.username
        
        # Prepare context
        context = {
            'user': user,
            'user_name': user_name,
            'sos_alert': sos_alert,
            'alert_type_display': sos_alert.get_alert_type_display(),
            'google_maps_url': f"https://maps.google.com/?q={sos_alert.latitude},{sos_alert.longitude}",
            'company_name': 'Nomado Travel',
            'support_email': settings.EMAIL_HOST_USER,
            'emergency_number': '112',  # Indian emergency number
        }
        
        # Render email templates
        html_content = render_to_string('emails/sos_alert.html', context)
        text_content = render_to_string('emails/sos_alert.txt', context)
        
        # Send to each emergency contact
        sent_count = 0
        for contact in emergency_contacts:
            try:
                # Create personalized context for each contact
                contact_context = context.copy()
                contact_context['contact'] = contact
                contact_context['contact_name'] = contact.name
                
                # Re-render templates with contact context
                html_content = render_to_string('emails/sos_alert.html', contact_context)
                text_content = render_to_string('emails/sos_alert.txt', contact_context)
                
                subject = f"🚨 EMERGENCY ALERT from {user_name} - Immediate Action Required"
                
                # Create email
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[contact.email]
                )
                msg.attach_alternative(html_content, "text/html")
                
                # Send email
                msg.send()
                sent_count += 1
                logger.info(f"SOS alert email sent to {contact.email} for alert {sos_alert.alert_id}")
                
            except Exception as e:
                logger.error(f"Failed to send SOS alert email to {contact.email}: {str(e)}")
        
        # Update alert with email status
        if sent_count > 0:
            sos_alert.emails_sent = True
            sos_alert.email_sent_at = timezone.now()
            sos_alert.save()
        
        return sent_count
        
    except Exception as e:
        logger.error(f"Failed to send SOS alert emails: {str(e)}")
        return 0

def send_location_share_email(location_share, emergency_contacts, additional_email=None):
    """Send location sharing email to emergency contacts"""
    try:
        user = location_share.user
        user_name = user.get_full_name() or user.username
        
        # Generate share URL (you'll need to implement this view)
        share_url = f"{settings.SITE_URL}/safety/shared/{location_share.share_id}/" if hasattr(settings, 'SITE_URL') else f"http://127.0.0.1:8000/safety/shared/{location_share.share_id}/"
        
        # Prepare context
        context = {
            'user': user,
            'user_name': user_name,
            'location_share': location_share,
            'share_url': share_url,
            'google_maps_url': f"https://maps.google.com/?q={location_share.latitude},{location_share.longitude}",
            'expires_at': location_share.expires_at,
            'duration_hours': location_share.duration_hours,
            'company_name': 'Nomado Travel',
            'support_email': settings.EMAIL_HOST_USER,
        }
        
        # Send to emergency contacts
        sent_count = 0
        email_list = []
        
        # Add emergency contacts
        for contact in emergency_contacts:
            email_list.append((contact.email, contact.name))
        
        # Add additional email if provided
        if additional_email:
            email_list.append((additional_email, 'Additional Contact'))
        
        for email, name in email_list:
            try:
                # Create personalized context
                contact_context = context.copy()
                contact_context['contact_name'] = name
                
                # Render email templates
                html_content = render_to_string('emails/location_share.html', contact_context)
                text_content = render_to_string('emails/location_share.txt', contact_context)
                
                subject = f"📍 {user_name} is sharing their live location with you"
                
                # Create email
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                msg.attach_alternative(html_content, "text/html")
                
                # Send email
                msg.send()
                sent_count += 1
                logger.info(f"Location share email sent to {email} for share {location_share.share_id}")
                
            except Exception as e:
                logger.error(f"Failed to send location share email to {email}: {str(e)}")
        
        # Update location share with email status
        if sent_count > 0:
            location_share.emails_sent = True
            location_share.email_sent_at = timezone.now()
            location_share.save()
        
        return sent_count
        
    except Exception as e:
        logger.error(f"Failed to send location share emails: {str(e)}")
        return 0

def send_safety_checkin_email(safety_checkin, emergency_contacts):
    """Send safety check-in email to emergency contacts"""
    try:
        user = safety_checkin.user
        user_name = user.get_full_name() or user.username
        
        # Only send emails for CONCERN or EMERGENCY status
        if safety_checkin.status == 'SAFE':
            return 0
        
        # Prepare context
        context = {
            'user': user,
            'user_name': user_name,
            'safety_checkin': safety_checkin,
            'status_display': safety_checkin.get_status_display(),
            'google_maps_url': f"https://maps.google.com/?q={safety_checkin.latitude},{safety_checkin.longitude}",
            'company_name': 'Nomado Travel',
            'support_email': settings.EMAIL_HOST_USER,
            'is_emergency': safety_checkin.status == 'EMERGENCY',
            'is_concern': safety_checkin.status == 'CONCERN',
        }
        
        # Send to each emergency contact
        sent_count = 0
        for contact in emergency_contacts:
            try:
                # Create personalized context for each contact
                contact_context = context.copy()
                contact_context['contact'] = contact
                contact_context['contact_name'] = contact.name
                
                # Render email templates
                html_content = render_to_string('emails/safety_checkin.html', contact_context)
                text_content = render_to_string('emails/safety_checkin.txt', contact_context)
                
                # Set subject based on status
                if safety_checkin.status == 'EMERGENCY':
                    subject = f"🚨 EMERGENCY Check-in from {user_name} - Immediate Attention Required"
                else:
                    subject = f"⚠️ Safety Concern from {user_name} - Please Check"
                
                # Create email
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[contact.email]
                )
                msg.attach_alternative(html_content, "text/html")
                
                # Send email
                msg.send()
                sent_count += 1
                logger.info(f"Safety check-in email sent to {contact.email} for checkin by {user.username}")
                
            except Exception as e:
                logger.error(f"Failed to send safety check-in email to {contact.email}: {str(e)}")
        
        # Update check-in with email status
        if sent_count > 0:
            safety_checkin.emails_sent = True
            safety_checkin.email_sent_at = timezone.now()
            safety_checkin.save()
        
        return sent_count
        
    except Exception as e:
        logger.error(f"Failed to send safety check-in emails: {str(e)}")
        return 0

def send_alert_status_update_email(sos_alert, emergency_contacts, updated_by=None):
    """Send email when SOS alert status is updated (resolved, false alarm, etc.)"""
    try:
        user = sos_alert.user
        user_name = user.get_full_name() or user.username
        
        # Prepare context
        context = {
            'user': user,
            'user_name': user_name,
            'sos_alert': sos_alert,
            'status_display': sos_alert.get_status_display(),
            'updated_by': updated_by,
            'company_name': 'Nomado Travel',
            'support_email': settings.EMAIL_HOST_USER,
        }
        
        # Send to each emergency contact
        sent_count = 0
        for contact in emergency_contacts:
            try:
                # Create personalized context
                contact_context = context.copy()
                contact_context['contact'] = contact
                contact_context['contact_name'] = contact.name
                
                # Render email templates
                html_content = render_to_string('emails/alert_status_update.html', contact_context)
                text_content = render_to_string('emails/alert_status_update.txt', contact_context)
                
                subject = f"✅ Update: Emergency Alert from {user_name} - {sos_alert.get_status_display()}"
                
                # Create email
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[contact.email]
                )
                msg.attach_alternative(html_content, "text/html")
                
                # Send email
                msg.send()
                sent_count += 1
                logger.info(f"Alert status update email sent to {contact.email} for alert {sos_alert.alert_id}")
                
            except Exception as e:
                logger.error(f"Failed to send status update email to {contact.email}: {str(e)}")
        
        return sent_count
        
    except Exception as e:
        logger.error(f"Failed to send alert status update emails: {str(e)}")
        return 0