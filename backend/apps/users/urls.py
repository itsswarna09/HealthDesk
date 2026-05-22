"""
HealthDesk — Users App URL Configuration
==========================================
All auth-related endpoints for the users app.
Mounted at: /api/v1/auth/
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserProfileView,
    ChangePasswordView,
)

app_name = 'users'

urlpatterns = [
    # ── Registration & Login ──────────────────────────────────────────────────
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # ── Token Management ──────────────────────────────────────────────────────
    # TokenRefreshView is from simplejwt — handles refresh token → new access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # ── Profile ───────────────────────────────────────────────────────────────
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserProfileView.as_view(), name='profile-update'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
