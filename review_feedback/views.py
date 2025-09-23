from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def reviews_dashboard_view(request):
    return render(request, 'review_feedback/dashboard.html')

@login_required
def hotel_review_view(request, hotel_id):
    return render(request, 'review_feedback/hotel_review.html')

@login_required
def transport_review_view(request, route_id):
    return render(request, 'review_feedback/transport_review.html')

@login_required
def feedback_view(request):
    return render(request, 'review_feedback/feedback.html')