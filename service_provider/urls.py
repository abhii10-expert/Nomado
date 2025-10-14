from django.urls import path
from . import views

urlpatterns = [
    path('', views.provider_dashboard_view, name='provider_dashboard'),
    path('register/', views.provider_register_view, name='provider_register'),
    
    # Hotels
    path('hotels/', views.provider_hotels_view, name='provider_hotels'),
    path('hotels/add/', views.provider_add_hotel_view, name='provider_add_hotel'),
    path('hotels/<int:hotel_id>/edit/', views.provider_edit_hotel_view, name='provider_edit_hotel'),
    
    # Transport
    path('transport/', views.provider_transport_view, name='provider_transport'),
    path('transport/add/', views.provider_add_route_view, name='provider_add_route'),
    path('transport/<int:route_id>/edit/', views.provider_edit_route_view, name='provider_edit_route'),
    
    # Other
    path('bookings/', views.provider_bookings_view, name='provider_bookings'),
    path('earnings/', views.provider_earnings_view, name='provider_earnings'),
]