"""
HealthDesk — Core Utils: API Response Helpers
================================================
Consistent response structure across all API endpoints.

WHY standardized responses?
The Angular frontend (and any future mobile app) can rely on a
predictable response shape. This prevents scattered response formats
across different endpoints.

Standard response shape:
{
    "success": true/false,
    "message": "Human-readable message",
    "data": {...},           # Present on success
    "errors": {...},         # Present on failure
    "meta": {                # Present on paginated responses
        "count": 50,
        "page": 1,
        "total_pages": 3
    }
}
"""

from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """Helper class for creating standardized API responses."""

    @staticmethod
    def success(data=None, message='Success', status_code=status.HTTP_200_OK, meta=None):
        """Return a standardized success response."""
        response_data = {
            'success': True,
            'message': message,
        }
        if data is not None:
            response_data['data'] = data
        if meta is not None:
            response_data['meta'] = meta

        return Response(response_data, status=status_code)

    @staticmethod
    def error(message='An error occurred', errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Return a standardized error response."""
        response_data = {
            'success': False,
            'message': message,
        }
        if errors is not None:
            response_data['errors'] = errors

        return Response(response_data, status=status_code)

    @staticmethod
    def created(data=None, message='Created successfully'):
        """Shortcut for 201 Created responses."""
        return APIResponse.success(data=data, message=message, status_code=status.HTTP_201_CREATED)

    @staticmethod
    def not_found(message='Resource not found'):
        """Shortcut for 404 responses."""
        return APIResponse.error(message=message, status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def forbidden(message='You do not have permission to perform this action'):
        """Shortcut for 403 responses."""
        return APIResponse.error(message=message, status_code=status.HTTP_403_FORBIDDEN)
