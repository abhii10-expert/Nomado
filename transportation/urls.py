from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.transport_search_view, name='transport_search'),
    path('route/<int:route_id>/', views.route_detail_view, name='route_detail'),
    path('route/<int:route_id>/book/', views.transport_booking_view, name='transport_booking'),
    # REMOVED: Old payment URLs - now using centralized payment system  
    # path('payment/<str:booking_id>/', views.transport_payment_view, name='transport_payment'),
    # path('verify-payment/', views.verify_transport_payment, name='verify_transport_payment'),
    path('booking/<str:booking_id>/', views.transport_booking_confirmation_view, name='transport_booking_confirmation'),
    path('my-bookings/', views.my_transport_bookings_view, name='my_transport_bookings'),
    path('cancel/<str:booking_id>/', views.cancel_transport_booking_view, name='cancel_transport_booking'),
]