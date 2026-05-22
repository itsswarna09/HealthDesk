import os
import uuid
import django
from datetime import datetime, timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthdesk.settings')
django.setup()

from django.conf import settings
from apps.users.models import UserDocument
from apps.records.models import MedicalRecordDocument

print("Finding patient Dean Winchester...")
dean = UserDocument.find_by_email('patient.dean@demo.com')
if not dean:
    print("Dean not found. Run seed_data.py first.")
    exit(1)

patient_id = str(dean['_id'])
print(f"Dean's patient ID is: {patient_id}")

# Create directories if they do not exist
records_dir = os.path.join(settings.MEDIA_ROOT, 'medical_records', patient_id)
os.makedirs(records_dir, exist_ok=True)

# Define mock records
mock_files = [
    {
        'title': 'Allergy Prescription - Dr. Alice Smith',
        'category': 'Prescription',
        'description': 'Antihistamines and nasal spray prescription for seasonal allergies.',
        'doctor_name': 'Dr. Alice Smith',
        'record_date': '2026-05-10',
        'file_name': 'prescription_may_2026.pdf',
        'content': '%PDF-1.4\n%... Mock Prescription PDF ...\n',
        'file_type': 'application/pdf'
    },
    {
        'title': 'Complete Blood Count (CBC) Report',
        'category': 'Blood Test',
        'description': 'Routine annual health check blood profile showing normal lipid and hematology panels.',
        'doctor_name': 'Dr. Bob Jones',
        'record_date': '2026-04-18',
        'file_name': 'blood_report_cbc.pdf',
        'content': '%PDF-1.4\n%... Mock Blood Report PDF ...\n',
        'file_type': 'application/pdf'
    },
    {
        'title': 'Chest X-Ray Scan - Fracture Rule Out',
        'category': 'Scan / X-Ray',
        'description': 'X-Ray imaging following a mild chest strain during outdoor hiking. Results: No signs of pleural effusion or bone fracture.',
        'doctor_name': 'Dr. Evan Wright',
        'record_date': '2026-03-22',
        'file_name': 'chest_xray_scan.png',
        'content': b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB\x82',
        'file_type': 'image/png'
    }
]

# Clean existing records first to avoid duplicates
MedicalRecordDocument.collection().delete_many({'patient_id': dean['_id']})

for r in mock_files:
    ext = os.path.splitext(r['file_name'])[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(records_dir, unique_name)
    
    # Write mock content to file
    mode = 'wb' if isinstance(r['content'], bytes) else 'w'
    with open(file_path, mode) as f:
        f.write(r['content'])
        
    relative_path = os.path.join('medical_records', patient_id, unique_name)
    file_size = os.path.getsize(file_path)
    
    doc = MedicalRecordDocument.create({
        'patient_id': patient_id,
        'title': r['title'],
        'category': r['category'],
        'description': r['description'],
        'doctor_name': r['doctor_name'],
        'record_date': r['record_date'],
        'file_name': r['file_name'],
        'file_path': relative_path,
        'file_size': file_size,
        'file_type': r['file_type']
    })
    print(f"Created Record: {r['title']} -> {relative_path}")

print("Seeding medical records completed successfully!")
