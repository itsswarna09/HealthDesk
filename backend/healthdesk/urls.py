"""
HealthDesk — Root URL Configuration
=====================================
All URLs are versioned under /api/v1/ for future API versioning.

WHY versioning from day one?
When we ship breaking API changes in v2, v1 clients (mobile apps,
third-party integrations) won't break. This is standard practice.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin — internal dashboard for admins
    path('admin/', admin.site.urls),

    # API v1 — all application routes
    path('api/v1/', include('healthdesk.api_router')),
]

# ─── Development-only: serve media files ─────────────────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
