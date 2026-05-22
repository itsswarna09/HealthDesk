from django.urls import path

from .views import (
    DoctorListView,
    SpecializationListView,
    DoctorDetailView,
    DoctorProfileUpdateView,
    AppointmentView,
    AppointmentDetailView,
    AppointmentDetailView,
    AppointmentStatusView,
    AppointmentCancelView,
    DoctorAvailabilityUpdateView,
    DoctorSlotsView,
)

app_name = 'appointments'

urlpatterns = [
    # ── Doctors ───────────────────────────────────────────────────────────────
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('doctors/specializations/', SpecializationListView.as_view(), name='specialization-list'),
    path('doctors/profile/', DoctorProfileUpdateView.as_view(), name='doctor-profile-update'),
    path('doctors/availability/', DoctorAvailabilityUpdateView.as_view(), name='doctor-availability-update'),
    path('doctors/<str:doctor_id>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('doctors/<str:doctor_id>/slots/', DoctorSlotsView.as_view(), name='doctor-slots'),

    # ── Appointments ──────────────────────────────────────────────────────────
    path('', AppointmentView.as_view(), name='appointment-list-create'),
    path('<str:app_id>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('<str:app_id>/status/', AppointmentStatusView.as_view(), name='appointment-status-update'),
    path('<str:app_id>/cancel/', AppointmentCancelView.as_view(), name='appointment-cancel'),
]
