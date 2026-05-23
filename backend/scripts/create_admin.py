import bcrypt, importlib.util, sys
from pymongo import MongoClient
from pathlib import Path

# Load Django settings
settings_path = Path('e:/HealthDesk/backend/healthdesk/settings.py')
spec = importlib.util.spec_from_file_location('settings', str(settings_path))
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)

client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
db = client[settings.MONGO_DB_NAME]
users = db['users']

email = 'admin@gmail.com'
password = 'admin12345'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

user_doc = {
    'full_name': 'Admin User',
    'email': email,
    'password': hashed,
    'role': 'ADMIN',
    'phone': '',
    'gender': '',
    'dob': None,
    'blood_group': '',
    'address': {},
    'emergency_contact': {},
    'donor_available': False,
}

result = users.replace_one({'email': email}, user_doc, upsert=True)
print('MongoDB admin insertion result:', result.matched_count, result.modified_count, result.upserted_id)
