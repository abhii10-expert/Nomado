from django.urls import path
from . import views

urlpatterns = [
    path('', views.location_dashboard_view, name='location_share'),
    path('dashboard/', views.location_dashboard_view, name='location_dashboard'),
    path('emergency-contacts/', views.emergency_contacts_view, name='emergency_contacts'),
    path('share-location/', views.location_share_view, name='share_location'),
    path('sos-alerts/', views.sos_alerts_view, name='sos_alerts'),
    path('safety-checkin/', views.safety_checkin_view, name='safety_checkin'),
    
    # AJAX endpoints
    path('ajax/share-location/', views.share_location_ajax, name='share_location_ajax'),
    path('ajax/trigger-sos/', views.trigger_sos_ajax, name='trigger_sos_ajax'),
    path('ajax/safety-checkin/', views.safety_checkin_ajax, name='safety_checkin_ajax'),
    
    # Public location view
    path('shared/<uuid:share_id>/', views.view_shared_location, name='view_shared_location'),
]