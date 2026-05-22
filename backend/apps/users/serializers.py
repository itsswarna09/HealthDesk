"""
HealthDesk — User Serializers (DRF + pymongo)
================================================
These serializers handle request validation and response formatting.
They do NOT use Django ModelSerializer since our data is in MongoDB.
Instead they are plain Serializer classes with explicit fields.

Flow:
  Incoming JSON → Serializer.is_valid() → validated_data → UserDocument.create()
  MongoDB doc   → UserDocument.serialize() → JSON response
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

from .models import UserDocument, Role, BloodGroup


class RegisterSerializer(serializers.Serializer):
    """
    Validates new user registration data.
    Password strength validated by Django's built-in validators.
    """

    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    role = serializers.ChoiceField(
        choices=[(r, r) for r in Role.ALL],
        default=Role.PATIENT,
        required=False
    )
    blood_group = serializers.ChoiceField(
        choices=[(b, b) for b in BloodGroup.ALL],
        default=BloodGroup.UNKNOWN,
        required=False
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label='Confirm Password',
        style={'input_type': 'password'}
    )

    def validate_email(self, value):
        """Check email is not already registered."""
        email = value.lower().strip()
        if UserDocument.find_by_email(email):
            raise serializers.ValidationError(
                'An account with this email address already exists.'
            )
        return email

    def validate_password(self, value):
        """Run Django's password strength validators."""
        validate_password(value)
        return value

    def validate(self, attrs):
        """Cross-field validation: password match."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })
        return attrs


class LoginSerializer(serializers.Serializer):
    """Simple login credentials serializer."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )


class UserProfileSerializer(serializers.Serializer):
    """
    Read/update user profile.
    Used for GET /profile/ and PUT /profile/update/ responses.
    """

    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True, allow_null=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    blood_group = serializers.ChoiceField(
        choices=[(b, b) for b in BloodGroup.ALL],
        required=False
    )
    blood_donor_available = serializers.BooleanField(required=False)
    emergency_contact_name = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    emergency_contact_phone = serializers.CharField(max_length=15, required=False, allow_blank=True, allow_null=True)
    
    # Address fields passed flat for simplicity in update, combined in view or model
    address_street = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    address_city = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    address_state = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    address_zip = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Handles authenticated password change requests."""

    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password2 = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password': 'New passwords do not match.'})
        return attrs
