from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('hotels/', views.hotel_search_view, name='hotel_search'),
    path('transport/', views.transport_search_view, name='transport_search'),
    path('location/', views.location_share_view, name='location_share'),
]