import razorpay
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_razorpay_client():
    """Get Razorpay client instance"""
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_razorpay_order(amount, currency='INR', receipt=None, notes=None):
    """Create a Razorpay order"""
    try:
        client = get_razorpay_client()
        
        order_data = {
            'amount': int(amount * 100),  # Convert to paisa
            'currency': currency,
            'payment_capture': 1  # Auto capture payment
        }
        
        if receipt:
            order_data['receipt'] = receipt
        if notes:
            order_data['notes'] = notes
            
        order = client.order.create(order_data)
        return {
            'success': True,
            'order': order
        }
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """Verify Razorpay payment signature"""
    try:
        client = get_razorpay_client()
        
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        client.utility.verify_payment_signature(params_dict)
        return {
            'success': True,
            'verified': True
        }
    except Exception as e:
        logger.error(f"Razorpay signature verification failed: {str(e)}")
        return {
            'success': False,
            'verified': False,
            'error': str(e)
        }

def get_payment_details(payment_id):
    """Get payment details from Razorpay"""
    try:
        client = get_razorpay_client()
        payment = client.payment.fetch(payment_id)
        return {
            'success': True,
            'payment': payment
        }
    except Exception as e:
        logger.error(f"Failed to fetch payment details: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }