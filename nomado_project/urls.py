from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user_management.urls')),
    path('hotels/', include('hotel_booking.urls')),
    path('transport/', include('transportation.urls')),
    path('safety/', include('location_sos.urls')),
    path('payments/', include('payment_management.urls')),
    path('reviews/', include('review_feedback.urls')),
    path('providers/', include('service_provider.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)