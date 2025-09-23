from django.urls import path
from . import views

urlpatterns = [
    path('', views.provider_dashboard_view, name='provider_dashboard'),
    path('register/', views.provider_register_view, name='provider_register'),
    path('hotels/', views.provider_hotels_view, name='provider_hotels'),
    path('transport/', views.provider_transport_view, name='provider_transport'),
    path('bookings/', views.provider_bookings_view, name='provider_bookings'),
    path('earnings/', views.provider_earnings_view, name='provider_earnings'),
]