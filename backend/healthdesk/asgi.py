"""
HealthDesk ASGI Configuration
(For future WebSocket support — emergency alerts, real-time notifications)
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthdesk.settings')
application = get_asgi_application()
