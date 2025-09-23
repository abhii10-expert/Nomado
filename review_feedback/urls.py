from django.urls import path
from . import views

urlpatterns = [
    path('', views.reviews_dashboard_view, name='reviews_dashboard'),
    path('hotel/<int:hotel_id>/', views.hotel_review_view, name='hotel_review'),
    path('transport/<int:route_id>/', views.transport_review_view, name='transport_review'),
    path('feedback/', views.feedback_view, name='feedback'),
]