"""
HealthDesk — API v1 Router
============================
Central registry for all v1 API endpoints.
Adding a new app's URLs here is the only integration step needed.

Pattern: Each app manages its own urls.py
This router just assembles them under /api/v1/
"""

from django.urls import path, include

urlpatterns = [
    # ── Authentication & Users ──────────────────────────────────────────────
    path('auth/', include('apps.users.urls')),

    # ── Phase 2+ (uncomment as features are built) ──────────────────────────
    path('appointments/', include('apps.appointments.urls')),
    path('records/', include('apps.records.urls')),
    path('blood-requests/', include('apps.blood_requests.urls')),
    # path('emergency/', include('apps.emergency.urls')),
]
