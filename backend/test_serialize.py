import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthdesk.settings')

import django
django.setup()

from apps.users.models import UserDocument
from apps.appointments.models import DoctorDocument

doc = DoctorDocument.collection().find_one()
print("Raw doc:", doc)
print("user_id type:", type(doc.get('user_id')))
serialized = DoctorDocument.serialize(doc, include_user=True)
print("Serialized:", serialized)
