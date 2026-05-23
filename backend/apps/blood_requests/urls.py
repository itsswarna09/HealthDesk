from django.urls import path
from .views import (
    BloodDonorView,
    BloodDonorListView,
    BloodRequestListView,
    BloodRequestDetailView,
    BloodOptionsView
)

app_name = 'blood_requests'

urlpatterns = [
    path('donors/me/', BloodDonorView.as_view(), name='donor-me'),
    path('donors/', BloodDonorListView.as_view(), name='donor-list'),
    path('requests/', BloodRequestListView.as_view(), name='request-list'),
    path('requests/<str:req_id>/', BloodRequestDetailView.as_view(), name='request-detail'),
    path('options/', BloodOptionsView.as_view(), name='options'),
]
