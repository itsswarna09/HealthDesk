"""
Users app configuration.
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'User Management'

    def ready(self):
        """
        Called when Django starts.
        Ensure MongoDB indexes are created on startup.
        """
        try:
            from .models import UserDocument
            UserDocument.ensure_indexes()
        except Exception:
            # Gracefully skip if MongoDB is not available at startup
            # (e.g., during migrations or CI without MongoDB)
            pass
