"""
HealthDesk — User Auth Views
==============================
Authentication endpoints for Phase 1.

Endpoints:
  POST /api/v1/auth/register/
  POST /api/v1/auth/login/
  POST /api/v1/auth/logout/
  POST /api/v1/auth/token/refresh/
  GET  /api/v1/auth/profile/
  PUT  /api/v1/auth/profile/update/
  PUT  /api/v1/auth/change-password/
"""

import logging
from datetime import datetime, timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.utils.api_response import APIResponse
from .models import UserDocument
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

logger = logging.getLogger(__name__)


def generate_tokens(user_data: dict) -> dict:
    """
    Generate JWT access + refresh tokens for a MongoDB user.
    Embeds role and email as custom claims so the frontend
    doesn't need a separate profile call just to know the role.
    """
    refresh = RefreshToken()
    
    # SimpleJWT expects user_id in the payload
    refresh['user_id'] = user_data['id']
    
    # Embed extra claims into the token payload
    refresh['email'] = user_data['email']
    refresh['role'] = user_data['role']
    refresh['full_name'] = user_data.get('full_name', '')

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    """POST /api/v1/auth/register/ — public."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error('Registration failed.', errors=serializer.errors)

        data = serializer.validated_data
        data.pop('password2')

        user_doc = UserDocument.create(data)
        user_data = UserDocument.serialize(user_doc)
        tokens = generate_tokens(user_data)

        logger.info(f"New user registered: {user_data['email']}")
        return APIResponse.created(data={'user': user_data, 'tokens': tokens},
                                   message='Account created successfully. Welcome to HealthDesk!')


class LoginView(APIView):
    """POST /api/v1/auth/login/ — public."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error('Invalid login data.', errors=serializer.errors)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user_doc = UserDocument.find_by_email(email)
        if not user_doc:
            return APIResponse.error('No account found with this email address.',
                                     status_code=status.HTTP_401_UNAUTHORIZED)

        if not UserDocument.check_password(password, user_doc.get('password_hash', '')):
            return APIResponse.error('Incorrect password.',
                                     status_code=status.HTTP_401_UNAUTHORIZED)

        if not user_doc.get('is_active', True):
            return APIResponse.error('This account has been deactivated. Contact support.',
                                     status_code=status.HTTP_403_FORBIDDEN)

        # Update last login timestamp
        UserDocument.update(str(user_doc['_id']), {'last_login': datetime.now(timezone.utc)})

        user_data = UserDocument.serialize(user_doc)
        tokens = generate_tokens(user_data)

        logger.info(f"User logged in: {email}")
        return APIResponse.success(data={'user': user_data, 'tokens': tokens},
                                   message='Login successful.')


class LogoutView(APIView):
    """POST /api/v1/auth/logout/ — frontend handles token deletion."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return APIResponse.success(message='Logged out successfully.')


class UserProfileView(APIView):
    """
    GET /api/v1/auth/profile/        — get own profile
    PUT /api/v1/auth/profile/update/ — update own profile
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_doc = UserDocument.find_by_id(str(request.user.id))
        if not user_doc:
            return APIResponse.not_found('User profile not found.')
        return APIResponse.success(data={'user': UserDocument.serialize(user_doc)})

    def put(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error('Invalid data.', errors=serializer.errors)

        val_data = serializer.validated_data.copy()
        
        # Convert flat keys to MongoDB dot notation for nested objects
        dot_notation_data = {}
        for key, value in val_data.items():
            if key.startswith('emergency_contact_'):
                nested_key = key.replace('emergency_contact_', '')
                dot_notation_data[f'emergency_contact.{nested_key}'] = value
            elif key.startswith('address_'):
                nested_key = key.replace('address_', '')
                dot_notation_data[f'address.{nested_key}'] = value
            else:
                dot_notation_data[key] = value

        UserDocument.update(str(request.user.id), dot_notation_data)
        user_doc = UserDocument.find_by_id(str(request.user.id))
        return APIResponse.success(data={'user': UserDocument.serialize(user_doc)},
                                   message='Profile updated successfully.')


class ChangePasswordView(APIView):
    """PUT /api/v1/auth/change-password/"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error('Invalid data.', errors=serializer.errors)

        user_doc = UserDocument.find_by_id(str(request.user.id))
        if not UserDocument.check_password(
            serializer.validated_data['old_password'],
            user_doc.get('password_hash', '')
        ):
            return APIResponse.error('Current password is incorrect.')

        new_hash = UserDocument.hash_password(serializer.validated_data['new_password'])
        UserDocument.collection().update_one(
            {'_id': user_doc['_id']},
            {'$set': {'password_hash': new_hash}}
        )
        return APIResponse.success(message='Password changed. Please log in with your new password.')
