from django.urls import path
from . import views

urlpatterns = [
    # ORIGINAL URLs
    path('', views.payment_dashboard_view, name='payment_dashboard'),
    path('methods/', views.payment_methods_view, name='payment_methods'),
    path('history/', views.transaction_history_view, name='transaction_history'),
    
    # PAYMENT PROCESSING URLs
    path('process/', views.process_payment_view, name='process_payment'),
    path('payment/<uuid:transaction_id>/', views.payment_page_view, name='payment_page'),
    path('verify/', views.verify_payment_view, name='verify_payment'),
    path('success/<uuid:transaction_id>/', views.payment_success_view, name='payment_success'),
    path('failure/<uuid:transaction_id>/', views.payment_failure_view, name='payment_failure'),
    path('retry/<uuid:transaction_id>/', views.retry_payment_view, name='retry_payment'),
    
    # PAYMENT METHOD & RECEIPT URLs
    path('save-method/', views.save_payment_method_view, name='save_payment_method'),
    path('send-receipt/', views.send_email_receipt_view, name='send_email_receipt'),
    path('make-primary/', views.make_primary_payment_method_view, name='make_primary_payment_method'),
    path('delete-method/', views.delete_payment_method_view, name='delete_payment_method'),
    path('test-email/', views.test_email_function, name='test_email'),
]