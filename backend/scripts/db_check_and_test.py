import importlib.util
import sys
from pathlib import Path
import bcrypt
from pymongo import MongoClient, ASCENDING

# Load Django settings to get MongoDB connection info
settings_path = Path('e:/HealthDesk/backend/healthdesk/settings.py')
spec = importlib.util.spec_from_file_location('settings', str(settings_path))
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)

# Connect to MongoDB
client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
db = client[settings.MONGO_DB_NAME]

# Expected collections and a minimal sample document for each
expected_collections = {
    'users': {
        'sample': {
            'full_name': 'Test User',
            'email': 'test_user@example.com',
            'password': bcrypt.hashpw('TestPass123!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'role': 'PATIENT',
            'phone': '1234567890',
            'gender': 'Other',
            'dob': None,
            'blood_group': 'O+',
            'address': {},
            'emergency_contact': {},
            'donor_available': False,
        },
        'unique_indexes': [('email', ASCENDING)],
    },
    'appointments': {
        'sample': {
            'patient_email': 'test_user@example.com',
            'doctor_email': 'doctor@example.com',
            'datetime': '2026-06-01T10:00:00Z',
            'status': 'PENDING',
        },
        'unique_indexes': [],
    },
    'records': {
        'sample': {
            'patient_email': 'test_user@example.com',
            'title': 'Blood Test',
            'description': 'Routine blood work',
            'file_url': 'http://example.com/blood_test.pdf',
        },
        'unique_indexes': [],
    },
    'blood_requests': {
        'sample': {
            'patient_email': 'test_user@example.com',
            'blood_group': 'A+',
            'quantity_ml': 500,
            'status': 'OPEN',
            'created_at': '2026-05-23T08:00:00Z',
        },
        'unique_indexes': [],
    },
    # add more collections as needed
}


def ensure_collection(name, cfg):
    coll = db[name]
    # Ensure unique indexes only if they don't already exist
    existing_indexes = coll.index_information()
    for fields, direction in cfg.get('unique_indexes', []):
        # Build the key pattern as a tuple of (field, direction)
        key_pattern = [(fields, direction)]
        # Check if any existing index has the same key pattern
        already_exists = any(info.get('key') == key_pattern for info in existing_indexes.values())
        if not already_exists:
            # Use deterministic name to keep consistency
            index_name = f"{name}_{fields}_unique"
            coll.create_index(key_pattern, unique=True, name=index_name)
    # Insert sample if collection is empty
    if coll.count_documents({}) == 0:
        coll.insert_one(cfg['sample'])
        print(f"Inserted sample document into '{name}' collection.")
    else:
        print(f"Collection '{name}' already has data (count={coll.count_documents({})}).")
    return coll


def crud_test(coll, sample_doc):
    # CREATE (already done via ensure_collection)
    # READ
    fetched = coll.find_one({list(sample_doc.keys())[0]: sample_doc[list(sample_doc.keys())[0]]})
    print(f"READ test for '{coll.name}':", fetched is not None)
    # UPDATE – add a temporary field
    update_result = coll.update_one({list(sample_doc.keys())[0]: sample_doc[list(sample_doc.keys())[0]]}, {'$set': {'_temp_test': True}})
    print(f"UPDATE modified count for '{coll.name}':", update_result.modified_count)
    # DELETE – remove the temp field
    delete_result = coll.update_one({list(sample_doc.keys())[0]: sample_doc[list(sample_doc.keys())[0]]}, {'$unset': {'_temp_test': ''}})
    print(f"CLEANUP (unset) modified count for '{coll.name}':", delete_result.modified_count)


def main():
    print('--- MongoDB inspection & CRUD test start ---')
    for coll_name, cfg in expected_collections.items():
        coll = ensure_collection(coll_name, cfg)
        crud_test(coll, cfg['sample'])
    print('--- All tests completed ---')

if __name__ == '__main__':
    main()
