from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('hotels/', views.hotel_search_view, name='hotel_search'),
    path('transport/', views.transport_search_view, name='transport_search'),
    path('location/', views.location_share_view, name='location_share'),
    
    # Admin management views - Changed paths to avoid conflict
    path('management/users/', views.users_list_view, name='admin_users_list'),
    path('management/admins/', views.admins_list_view, name='admin_admins_list'),
    path('management/user/<int:user_id>/', views.user_detail_view, name='admin_user_detail'),
    path('management/hotels/', views.hotels_list_view, name='admin_hotels_list'),
    path('management/routes/', views.routes_list_view, name='admin_routes_list'),
    path('management/hotel-bookings/', views.hotel_bookings_list_view, name='admin_hotel_bookings'),
    path('management/transport-bookings/', views.transport_bookings_list_view, name='admin_transport_bookings'),
]