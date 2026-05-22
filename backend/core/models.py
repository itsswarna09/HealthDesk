"""
HealthDesk — Core Utilities
==============================
Shared utilities used across all apps.
These are NOT app-specific — they belong in core/.

Contents:
- BaseModel: Abstract model with timestamps (used by all feature models)
- APIResponse: Standardized response format helper
"""

from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Abstract base model that adds created_at and updated_at to every model.

    WHY abstract model?
    Every feature model (Appointment, MedicalRecord, BloodRequest) needs
    timestamps. Inheritance from this base ensures consistency and saves
    repeating these fields in every model.

    Usage:
        class Appointment(TimestampedModel):
            # Gets created_at and updated_at automatically
            doctor = models.ForeignKey(...)
    """

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # No database table created for this model itself
        ordering = ['-created_at']
