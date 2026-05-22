"""
HealthDesk — Users App Admin
(Minimal — user data is in MongoDB, not Django ORM)
Admin panel is used for JWT token blacklist management in Phase 1.
Full user admin will be a custom admin dashboard in Phase 6.
"""
from django.contrib import admin

# JWT token blacklist entries are managed via the default admin
# registered automatically by rest_framework_simplejwt.token_blacklist
