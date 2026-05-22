"""
HealthDesk — MongoDB Connection Manager
=========================================
Central place to get a MongoDB database handle.

WHY this pattern?
- Single connection pool shared across the entire app (efficient)
- Settings-driven (swap local → Atlas by changing .env only)
- All app code calls `get_db()` — no hardcoded connection strings anywhere

Usage in any view or service:
    from core.db import get_db

    db = get_db()
    users_collection = db['users']
    user = users_collection.find_one({'email': 'test@example.com'})
"""

from pymongo import MongoClient
from django.conf import settings

_client = None


def get_mongo_client() -> MongoClient:
    """
    Returns a singleton MongoClient instance.
    Connection is created once and reused (connection pooling).
    """
    global _client
    if _client is None:
        _client = MongoClient(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT,
            # Connection pool settings (production-ready defaults)
            maxPoolSize=50,
            minPoolSize=5,
            serverSelectionTimeoutMS=5000,  # 5 second timeout to detect connection failure
        )
    return _client


def get_db():
    """
    Returns the HealthDesk MongoDB database instance.

    Example:
        db = get_db()
        db['users'].insert_one({...})
        db['appointments'].find({...})
    """
    client = get_mongo_client()
    return client[settings.MONGO_DB_NAME]


# ─── Collection Name Constants ────────────────────────────────────────────────
# Centralizing collection names prevents typos across the codebase.
# If you rename a collection, change it here — affects everywhere.
class Collections:
    USERS = 'users'
    APPOINTMENTS = 'appointments'
    MEDICAL_RECORDS = 'medical_records'
    BLOOD_REQUESTS = 'blood_requests'
    EMERGENCY_REQUESTS = 'emergency_requests'
    DOCTORS = 'doctors'
