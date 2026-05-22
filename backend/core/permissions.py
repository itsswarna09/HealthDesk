"""
HealthDesk — Core Permissions
================================
Custom DRF permission classes for role-based access control.

WHY custom permissions?
DRF's built-in IsAuthenticated only checks if a user is logged in.
HealthDesk needs role-based checks: doctors can see patient records,
only donors appear in blood request matches, etc.

WHY reading from token payload?
Our users live in MongoDB, not Django ORM. The JWT token embeds a
'role' claim (set in generate_tokens_for_user in views.py). We read
that claim directly from request.auth (the validated token payload).

Usage in views:
    class AppointmentView(APIView):
        permission_classes = [IsAuthenticated, IsPatientOrDoctor]
"""

from rest_framework.permissions import BasePermission


def _get_role(request) -> str:
    """
    Extract the role from the JWT token payload.
    request.auth is the validated token object from simplejwt.
    Returns empty string if no role found (safe default — denies access).
    """
    if request.auth is None:
        return ''
    # simplejwt stores token payload accessible via dict-style access
    return request.auth.get('role', '')


class IsPatient(BasePermission):
    """Only PATIENT role users can access this endpoint."""
    message = 'Only patients can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            _get_role(request) == 'PATIENT'
        )


class IsDoctor(BasePermission):
    """Only DOCTOR role users can access this endpoint."""
    message = 'Only doctors can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            _get_role(request) == 'DOCTOR'
        )


class IsDonor(BasePermission):
    """Only DONOR role users can access this endpoint."""
    message = 'Only registered blood donors can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            _get_role(request) == 'DONOR'
        )


class IsPatientOrDoctor(BasePermission):
    """Patients AND doctors can access this endpoint (e.g., appointments)."""
    message = 'Only patients or doctors can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            _get_role(request) in ('PATIENT', 'DOCTOR')
        )


class IsAdminRole(BasePermission):
    """Only ADMIN role users can access this endpoint."""
    message = 'Only admins can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            _get_role(request) == 'ADMIN'
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: users can only access their OWN data,
    unless they are admin role.

    The owner check compares the 'user_id' JWT claim against the
    object's user_id field (a MongoDB ObjectId string).
    """
    message = 'You can only access your own data.'

    def has_object_permission(self, request, view, obj):
        # Admin bypass
        if _get_role(request) == 'ADMIN':
            return True
        # Get the requesting user's MongoDB ID from JWT
        request_user_id = str(request.auth.get('user_id', '')) if request.auth else ''
        # Check object ownership — handles both dict (MongoDB doc) and object
        if isinstance(obj, dict):
            return str(obj.get('user_id', obj.get('_id', ''))) == request_user_id
        if hasattr(obj, 'user_id'):
            return str(obj.user_id) == request_user_id
        return False
