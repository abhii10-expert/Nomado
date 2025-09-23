from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.hotel_search_view, name='hotel_search'),
    path('hotel/<int:hotel_id>/', views.hotel_detail_view, name='hotel_detail'),
    path('hotel/<int:hotel_id>/book/', views.hotel_booking_view, name='hotel_booking'),
    # REMOVED: Old payment URLs - now using centralized payment system
    # path('payment/<str:booking_id>/', views.hotel_payment_view, name='hotel_payment'),
    # path('verify-payment/', views.verify_hotel_payment, name='verify_hotel_payment'),
    path('booking/<str:booking_id>/', views.booking_confirmation_view, name='booking_confirmation'),
    path('my-bookings/', views.my_hotel_bookings_view, name='my_hotel_bookings'),
    path('cancel/<str:booking_id>/', views.cancel_hotel_booking_view, name='cancel_hotel_booking'),
]