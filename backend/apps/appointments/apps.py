from django.apps import AppConfig

class AppointmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.appointments'
    verbose_name = 'Appointments'

    def ready(self):
        """
        Called when Django starts.
        Ensure MongoDB indexes for doctors and appointments are created on startup.
        """
        try:
            from .models import DoctorDocument, AppointmentDocument
            DoctorDocument.ensure_indexes()
            AppointmentDocument.ensure_indexes()
        except Exception:
            # Gracefully skip if MongoDB is not available at startup
            pass

