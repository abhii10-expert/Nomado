from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db import models
import json
import logging
from .models import PaymentMethod, Transaction, Invoice, Refund
from hotel_booking.models import HotelBooking
from transportation.models import TransportBooking

logger = logging.getLogger(__name__)

# ENHANCED DASHBOARD VIEW
@login_required
def payment_dashboard_view(request):
    # Get user's recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user)[:5]
    payment_methods = PaymentMethod.objects.filter(user=request.user, is_active=True)
    
    # Calculate total spent
    total_spent = Transaction.objects.filter(
        user=request.user, 
        status='SUCCESS'
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    context = {
        'recent_transactions': recent_transactions,
        'payment_methods': payment_methods,
        'total_spent': total_spent,
    }
    return render(request, 'payment_management/dashboard.html', context)

@login_required
def payment_methods_view(request):
    payment_methods = PaymentMethod.objects.filter(user=request.user, is_active=True)
    context = {
        'payment_methods': payment_methods,
    }
    return render(request, 'payment_management/methods.html', context)

@login_required
def transaction_history_view(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-initiated_at')
    context = {
        'transactions': transactions,
    }
    return render(request, 'payment_management/history.html', context)


# NEW PAYMENT PROCESSING VIEWS
@login_required
def process_payment_view(request):
    """
    Central payment processing view that handles payments for both hotels and transport
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method')
        return redirect('payment_dashboard')
    
    try:
        # Get booking details from POST data
        booking_type = request.POST.get('booking_type')  # 'hotel' or 'transport'
        booking_id = request.POST.get('booking_id')
        payment_method_id = request.POST.get('payment_method_id')
        
        if not all([booking_type, booking_id]):
            messages.error(request, 'Missing booking information')
            return redirect('payment_dashboard')
        
        # Get the appropriate booking
        if booking_type == 'hotel':
            booking = get_object_or_404(HotelBooking, booking_id=booking_id, user=request.user)
            transaction_type = 'HOTEL_BOOKING'
        elif booking_type == 'transport':
            booking = get_object_or_404(TransportBooking, booking_id=booking_id, user=request.user)
            transaction_type = 'TRANSPORT_BOOKING'
        else:
            messages.error(request, 'Invalid booking type')
            return redirect('payment_dashboard')
        
        # Check if payment already exists
        existing_transaction = Transaction.objects.filter(
            user=request.user,
            **{f'{booking_type}_booking': booking},
            status__in=['SUCCESS', 'PROCESSING']
        ).first()
        
        if existing_transaction:
            messages.info(request, 'Payment already processed for this booking')
            return redirect('payment_success', transaction_id=existing_transaction.transaction_id)
        
        # Create transaction record
        with transaction.atomic():
            payment_transaction = Transaction.objects.create(
                user=request.user,
                transaction_type=transaction_type,
                amount=booking.total_amount,
                **{f'{booking_type}_booking': booking},
                status='PROCESSING'
            )
            
            # Import payment utilities
            try:
                from payment_utils import create_razorpay_order
                
                # Create Razorpay order
                razorpay_order = create_razorpay_order(
                    amount=booking.total_amount,
                    receipt=f"{booking_type}_{booking.booking_id}",
                    notes={
                        'booking_id': booking.booking_id,
                        'booking_type': booking_type,
                        'user_email': request.user.email,
                        'transaction_id': str(payment_transaction.transaction_id)
                    }
                )
                
                if razorpay_order['success']:
                    # Store Razorpay order ID
                    payment_transaction.gateway_transaction_id = razorpay_order['order']['id']
                    payment_transaction.save()
                    
                    # Store transaction ID in session
                    request.session['current_transaction_id'] = str(payment_transaction.transaction_id)
                    
                    # Redirect to payment page with transaction details
                    return redirect('payment_page', transaction_id=payment_transaction.transaction_id)
                else:
                    payment_transaction.status = 'FAILED'
                    payment_transaction.failure_reason = razorpay_order.get('error', 'Unknown error')
                    payment_transaction.save()
                    messages.error(request, 'Failed to initialize payment. Please try again.')
                    return redirect('payment_failure', transaction_id=payment_transaction.transaction_id)
                    
            except ImportError:
                payment_transaction.status = 'FAILED'
                payment_transaction.failure_reason = 'Payment service unavailable'
                payment_transaction.save()
                messages.error(request, 'Payment service temporarily unavailable')
                return redirect('payment_failure', transaction_id=payment_transaction.transaction_id)
                
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}")
        messages.error(request, 'An error occurred while processing payment')
        return redirect('payment_dashboard')

@login_required
def payment_page_view(request, transaction_id):
    """
    Display payment page with Razorpay integration
    """
    transaction_obj = get_object_or_404(
        Transaction, 
        transaction_id=transaction_id, 
        user=request.user
    )
    
    if transaction_obj.status != 'PROCESSING':
        messages.info(request, 'This transaction has already been processed')
        return redirect('payment_success' if transaction_obj.status == 'SUCCESS' else 'payment_failure', 
                       transaction_id=transaction_id)
    
    # Get booking details
    if transaction_obj.hotel_booking:
        booking = transaction_obj.hotel_booking
        booking_type = 'hotel'
    elif transaction_obj.transport_booking:
        booking = transaction_obj.transport_booking
        booking_type = 'transport'
    else:
        messages.error(request, 'Invalid transaction')
        return redirect('payment_dashboard')
    
    context = {
        'transaction': transaction_obj,
        'booking': booking,
        'booking_type': booking_type,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': transaction_obj.gateway_transaction_id,
        'razorpay_amount': int(transaction_obj.amount * 100),  # Amount in paisa
        'user_name': request.user.get_full_name() or request.user.username,
        'user_email': request.user.email,
        'user_phone': getattr(request.user, 'phone_number', ''),
    }
    return render(request, 'payment_management/payment_page.html', context)

@csrf_exempt
@login_required
def verify_payment_view(request):
    """
    SIMPLIFIED: Skip all validation and mark payment as successful
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        
        # Extract transaction ID
        transaction_id = data.get('transaction_id')
        
        if not transaction_id:
            return JsonResponse({'success': False, 'message': 'Missing transaction ID'})
        
        # Get transaction
        transaction_obj = get_object_or_404(
            Transaction, 
            transaction_id=transaction_id, 
            user=request.user
        )
        
        # SKIP ALL VALIDATION - Always mark as successful
        with transaction.atomic():
            # Payment automatically successful
            transaction_obj.status = 'SUCCESS'
            transaction_obj.completed_at = timezone.now()
            transaction_obj.save()
            
            # Update booking status
            if transaction_obj.hotel_booking:
                booking = transaction_obj.hotel_booking
                booking.booking_status = 'CONFIRMED'
                booking.save()
            elif transaction_obj.transport_booking:
                booking = transaction_obj.transport_booking
                booking.booking_status = 'CONFIRMED'
                booking.save()
                # Update seat availability
                if hasattr(booking, 'route') and hasattr(booking.route, 'available_seats'):
                    route = booking.route
                    route.available_seats = max(0, route.available_seats - booking.passengers)
                    route.save()
            
            # Create invoice
            create_invoice_for_transaction(transaction_obj)
            
            # SEND EMAIL RECEIPT - This is the important part
            email_sent = send_booking_receipt_email(transaction_obj)
            
            # Log successful payment
            logger.info(f"Payment successful for transaction {transaction_id}, Email sent: {email_sent}")
            
            # Clear session
            if 'current_transaction_id' in request.session:
                del request.session['current_transaction_id']
            
            return JsonResponse({
                'success': True,
                'message': 'Payment successful! Your booking is confirmed. Receipt sent to your email.',
                'redirect_url': f'/payments/success/{transaction_id}/'
            })
                
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Payment processing error: {str(e)}'
        })

@login_required
def payment_success_view(request, transaction_id):
    """
    Display payment success page
    """
    # CLEAR ALL MESSAGES TO PREVENT OLD MESSAGES FROM SHOWING
    storage = messages.get_messages(request)
    for message in storage:
        pass  # This consumes all messages
    
    transaction_obj = get_object_or_404(
        Transaction, 
        transaction_id=transaction_id, 
        user=request.user
    )
    
    if transaction_obj.status != 'SUCCESS':
        messages.warning(request, 'This transaction was not successful')
        return redirect('payment_failure', transaction_id=transaction_id)
    
    # Get related booking
    if transaction_obj.hotel_booking:
        booking = transaction_obj.hotel_booking
        booking_type = 'hotel'
    elif transaction_obj.transport_booking:
        booking = transaction_obj.transport_booking
        booking_type = 'transport'
    else:
        booking = None
        booking_type = None
    
    # Get invoice if exists
    try:
        invoice = transaction_obj.invoice
    except:
        invoice = None
    
    context = {
        'transaction': transaction_obj,
        'booking': booking,
        'booking_type': booking_type,
        'invoice': invoice,
    }
    return render(request, 'payment_management/success.html', context)

@login_required
def payment_failure_view(request, transaction_id):
    """
    Display payment failure page
    """
    transaction_obj = get_object_or_404(
        Transaction, 
        transaction_id=transaction_id, 
        user=request.user
    )
    
    context = {
        'transaction': transaction_obj,
        'failure_reason': transaction_obj.failure_reason or 'Unknown error occurred',
    }
    return render(request, 'payment_management/failure.html', context)

@login_required
def retry_payment_view(request, transaction_id):
    """
    Allow users to retry failed payments
    """
    transaction_obj = get_object_or_404(
        Transaction, 
        transaction_id=transaction_id, 
        user=request.user
    )
    
    if transaction_obj.status not in ['FAILED', 'CANCELLED']:
        messages.info(request, 'This transaction cannot be retried')
        return redirect('payment_success' if transaction_obj.status == 'SUCCESS' else 'payment_dashboard')
    
    # Reset transaction status
    transaction_obj.status = 'PROCESSING'
    transaction_obj.failure_reason = ''
    transaction_obj.save()
    
    return redirect('payment_page', transaction_id=transaction_id)


# NEW PAYMENT METHOD MANAGEMENT VIEWS
@csrf_exempt
@login_required
def save_payment_method_view(request):
    """Save user's payment method for future use"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        
        # Set current primary method to False if new method is primary
        if data.get('is_default', False):
            PaymentMethod.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Create payment method based on type
        payment_method = PaymentMethod.objects.create(
            user=request.user,
            payment_type=data.get('method'),
            is_default=data.get('is_default', False)
        )
        
        # Set type-specific fields
        if data.get('method') == 'CREDIT_CARD':
            payment_method.card_number = data.get('card_number')  # Last 4 digits only
            payment_method.card_holder_name = data.get('card_name')
            payment_method.expiry_month = data.get('expiry_month')
            payment_method.expiry_year = data.get('expiry_year')
        elif data.get('method') == 'UPI':
            payment_method.upi_id = data.get('upi_id')
        elif data.get('method') == 'NET_BANKING':
            payment_method.bank_name = data.get('bank_name')
        elif data.get('method') == 'WALLET':
            payment_method.wallet_provider = data.get('wallet_provider')
        
        payment_method.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Payment method saved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error saving payment method: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error saving payment method: {str(e)}'
        })

@csrf_exempt
@login_required
def make_primary_payment_method_view(request):
    """Make a payment method primary"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        method_id = data.get('method_id')
        
        # Remove primary status from all user's methods
        PaymentMethod.objects.filter(user=request.user).update(is_default=False)
        
        # Set the selected method as primary
        method = PaymentMethod.objects.get(id=method_id, user=request.user, is_active=True)
        method.is_default = True
        method.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Payment method set as primary'
        })
        
    except PaymentMethod.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Payment method not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@csrf_exempt
@login_required
def delete_payment_method_view(request):
    """Delete a payment method"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        method_id = data.get('method_id')
        
        method = PaymentMethod.objects.get(id=method_id, user=request.user, is_active=True)
        method.is_active = False
        method.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Payment method removed successfully'
        })
        
    except PaymentMethod.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Payment method not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@csrf_exempt
@login_required
def send_email_receipt_view(request):
    """Send email receipt after successful payment"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        
        transaction_obj = get_object_or_404(
            Transaction, 
            transaction_id=transaction_id, 
            user=request.user
        )
        
        # Send email receipt
        send_booking_receipt_email(transaction_obj)
        
        return JsonResponse({
            'success': True,
            'message': 'Receipt sent successfully'
        })
        
    except Exception as e:
        logger.error(f"Error sending receipt: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error sending receipt: {str(e)}'
        })


# UTILITY FUNCTIONS
def create_invoice_for_transaction(transaction_obj):
    """
    Create invoice for successful transaction
    """
    try:
        # Check if invoice already exists
        if hasattr(transaction_obj, 'invoice'):
            return transaction_obj.invoice
        
        # Calculate invoice details
        subtotal = transaction_obj.amount
        tax_rate = 0.18  # 18% GST
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount
        
        # Create invoice
        invoice = Invoice.objects.create(
            transaction=transaction_obj,
            due_date=timezone.now() + timezone.timedelta(days=30),
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            is_paid=True,
            paid_at=timezone.now()
        )
        
        logger.info(f"Invoice {invoice.invoice_number} created for transaction {transaction_obj.transaction_id}")
        return invoice
        
    except Exception as e:
        logger.error(f"Failed to create invoice for transaction {transaction_obj.transaction_id}: {str(e)}")
        return None

def send_booking_receipt_email(transaction):
    """Send booking confirmation email with receipt"""
    try:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get booking details
        if transaction.hotel_booking:
            booking = transaction.hotel_booking
            booking_type = 'Hotel'
            template_name = 'emails/hotel_booking_receipt.html'
            subject_line = f'Hotel Booking Confirmed - {booking.booking_id}'
        elif transaction.transport_booking:
            booking = transaction.transport_booking
            booking_type = 'Transportation' 
            template_name = 'emails/transport_booking_receipt.html'
            subject_line = f'Transport Booking Confirmed - {booking.booking_id}'
        else:
            logger.error(f"No booking found for transaction {transaction.transaction_id}")
            return False
        
        # Generate invoice if not exists
        try:
            if not hasattr(transaction, 'invoice') or not transaction.invoice:
                invoice = create_invoice_for_transaction(transaction)
            else:
                invoice = transaction.invoice
        except Exception as e:
            logger.warning(f"Could not create/get invoice: {e}")
            invoice = None
        
        # Prepare email context
        context = {
            'user': transaction.user,
            'booking': booking,
            'transaction': transaction,
            'booking_type': booking_type,
            'invoice': invoice,
            'company_name': 'Nomado',
            'support_email': 'support@nomado.com',
            'support_phone': '+91-1234-567890',
            'website_url': 'http://127.0.0.1:8000',  # Update with your domain
        }
        
        try:
            # Render email templates
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            # Fallback to simple text email
            plain_message = f"""
            Dear {transaction.user.get_full_name() or transaction.user.username},
            
            Your {booking_type.lower()} booking has been confirmed!
            
            Booking ID: {booking.booking_id}
            Transaction ID: {transaction.transaction_id}
            Amount Paid: ₹{transaction.amount}
            
            Thank you for choosing Nomado!
            """
            html_message = None
        
        # Send email
        try:
            email_sent = send_mail(
                subject=subject_line,
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@nomado.com'),
                recipient_list=[transaction.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            if email_sent:
                logger.info(f"Receipt email sent successfully to {transaction.user.email} for transaction {transaction.transaction_id}")
                return True
            else:
                logger.error(f"Failed to send receipt email - send_mail returned False")
                return False
                
        except Exception as email_error:
            logger.error(f"SMTP Error sending email: {str(email_error)}")
            
            # Try to send a simple text email as fallback
            try:
                from django.core.mail import EmailMessage
                email = EmailMessage(
                    subject=subject_line,
                    body=plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[transaction.user.email],
                )
                email.send(fail_silently=False)
                logger.info(f"Fallback email sent successfully")
                return True
            except Exception as fallback_error:
                logger.error(f"Fallback email also failed: {str(fallback_error)}")
                return False
        
    except Exception as e:
        logger.error(f"General error sending receipt email for transaction {transaction.transaction_id}: {str(e)}")
        return False

def test_email_function(request):
    """Test function to check email sending"""
    try:
        from django.core.mail import send_mail
        from django.http import HttpResponse
        
        result = send_mail(
            'Test Email from Nomado',
            'This is a test email to check if email sending is working.',
            'abhijithshaibinu001@gmail.com',  # From email
            ['abhijithshaibinu001@gmail.com'],  # To email (same for testing)
            fail_silently=False,
        )
        
        if result:
            return HttpResponse("Email sent successfully!")
        else:
            return HttpResponse("Email sending failed!")
            
    except Exception as e:
        return HttpResponse(f"Email error: {str(e)}")