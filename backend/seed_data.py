import os
import sys
import random
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthdesk.settings')
django.setup()

from apps.users.models import UserDocument, Role, BloodGroup
from apps.appointments.models import DoctorDocument, AppointmentDocument

print("Seeding demo doctors...")

doctors_data = [
    {"first": "Alice", "last": "Smith", "spec": "Cardiologist", "fee": 150, "gender": "Female"},
    {"first": "Bob", "last": "Jones", "spec": "Dermatologist", "fee": 120, "gender": "Male"},
    {"first": "Charlie", "last": "Brown", "spec": "Neurologist", "fee": 200, "gender": "Male"},
    {"first": "Diana", "last": "Prince", "spec": "Pediatrician", "fee": 100, "gender": "Female"},
    {"first": "Evan", "last": "Wright", "spec": "General Practitioner", "fee": 80, "gender": "Male"},
    {"first": "Fiona", "last": "Gallagher", "spec": "Orthopedist", "fee": 180, "gender": "Female"},
    {"first": "George", "last": "Miller", "spec": "Psychiatrist", "fee": 160, "gender": "Male"},
    {"first": "Hannah", "last": "Abbott", "spec": "Cardiologist", "fee": 150, "gender": "Female"},
    {"first": "Ian", "last": "Malcolm", "spec": "Endocrinologist", "fee": 170, "gender": "Male"},
    {"first": "Jane", "last": "Doe", "spec": "Gynecologist", "fee": 140, "gender": "Female"},
    {"first": "Kevin", "last": "Hart", "spec": "Pediatrician", "fee": 110, "gender": "Male"},
    {"first": "Laura", "last": "Palmer", "spec": "Dermatologist", "fee": 130, "gender": "Female"},
]

count = 0
for d in doctors_data:
    email = f"dr.{d['first'].lower()}.{d['last'].lower()}@demo.com"
    user_doc = UserDocument.find_by_email(email)
    
    if not user_doc:
        user_doc = UserDocument.create({
            'email': email,
            'password': 'Password123!',
            'first_name': d['first'],
            'last_name': d['last'],
            'role': Role.DOCTOR,
            'gender': d['gender'],
            'phone': f"+1555000{random.randint(1000, 9999)}",
            'address_city': "Metropolis",
            'address_state': "NY"
        })
        
        doc = DoctorDocument.create(user_doc['_id'], {
            'specialization': d['spec'],
            'experience_years': random.randint(5, 25),
            'consultation_fee': d['fee'],
            'qualifications': ["MBBS", "MD", "Fellowship"],
            'availability': [
                {"day": "Monday", "slots": ["09:00", "10:00", "11:00", "14:00"]},
                {"day": "Wednesday", "slots": ["10:00", "11:00", "15:00", "16:00"]},
                {"day": "Friday", "slots": ["09:00", "12:00", "13:00"]}
            ]
        })
        
        # Verify them so they show up in the listing
        DoctorDocument.update(doc['_id'], {'is_verified': True})
        count += 1

print(f"Successfully seeded {count} new demo doctors!")

print("Seeding demo patients...")
patients_data = [
    {"first": "Sam", "last": "Winchester", "gender": "Male"},
    {"first": "Dean", "last": "Winchester", "gender": "Male"},
    {"first": "Castiel", "last": "Angel", "gender": "Male"},
    {"first": "Mary", "last": "Poppins", "gender": "Female"},
]

p_count = 0
for p in patients_data:
    email = f"patient.{p['first'].lower()}@demo.com"
    if not UserDocument.find_by_email(email):
        UserDocument.create({
            'email': email,
            'password': 'Password123!',
            'first_name': p['first'],
            'last_name': p['last'],
            'role': Role.PATIENT,
            'gender': p['gender'],
            'blood_group': random.choice(BloodGroup.ALL)
        })
        p_count += 1

print(f"Successfully seeded {p_count} new demo patients!")
