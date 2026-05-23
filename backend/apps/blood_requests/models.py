from datetime import datetime, timezone
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
from core.db import get_db, Collections

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
URGENCY_LEVELS = ['Normal', 'Urgent', 'Emergency']
STATUS_CHOICES = ['Pending', 'Accepted', 'Rejected', 'Fulfilled', 'Closed']

class BloodDonorDocument:
    @staticmethod
    def collection():
        return get_db()[Collections.USERS] # Actually we might just use USERS collection or a separate one. Let's use a separate one: 'blood_donors'
        # Wait, core.db doesn't have BLOOD_DONORS. I will use 'blood_donors' directly.
        return get_db()['blood_donors']

    @staticmethod
    def register(user_id, data):
        now = datetime.now(timezone.utc)
        document = {
            'user_id': ObjectId(user_id),
            'blood_group': data['blood_group'],
            'city': data.get('city', '').strip().lower(),
            'phone': data.get('phone', ''),
            'last_donated_date': data.get('last_donated_date'),
            'is_available': data.get('is_available', True),
            'created_at': now,
            'updated_at': now,
        }
        
        existing = BloodDonorDocument.collection().find_one({'user_id': ObjectId(user_id)})
        if existing:
            document.pop('created_at')
            BloodDonorDocument.collection().update_one(
                {'_id': existing['_id']},
                {'$set': document}
            )
            document['_id'] = str(existing['_id'])
        else:
            result = BloodDonorDocument.collection().insert_one(document)
            document['_id'] = str(result.inserted_id)
            
        document['user_id'] = str(document['user_id'])
        return document

    @staticmethod
    def find_by_user(user_id):
        try:
            doc = BloodDonorDocument.collection().find_one({'user_id': ObjectId(user_id)})
            if doc:
                doc['_id'] = str(doc['_id'])
                doc['user_id'] = str(doc['user_id'])
            return doc
        except Exception:
            return None

    @staticmethod
    def get_donors(blood_group=None, city=None):
        query = {'is_available': True}
        if blood_group:
            query['blood_group'] = blood_group
        if city:
            query['city'] = city.strip().lower()
            
        pipeline = [
            {'$match': query},
            {'$lookup': {
                'from': Collections.USERS,
                'localField': 'user_id',
                'foreignField': '_id',
                'as': 'user'
            }},
            {'$unwind': '$user'},
            {'$sort': {'updated_at': DESCENDING}}
        ]
        
        docs = list(BloodDonorDocument.collection().aggregate(pipeline))
        for doc in docs:
            doc['_id'] = str(doc['_id'])
            doc['user_id'] = str(doc['user_id'])
            doc['user']['_id'] = str(doc['user']['_id'])
            if 'password' in doc['user']:
                del doc['user']['password']
        return docs

    @staticmethod
    def serialize(doc):
        if not doc:
            return {}
        return {
            'id': str(doc.get('_id', '')),
            'user_id': str(doc.get('user_id', '')),
            'blood_group': doc.get('blood_group', ''),
            'city': doc.get('city', '').title(),
            'phone': doc.get('phone', ''),
            'last_donated_date': doc.get('last_donated_date'),
            'is_available': doc.get('is_available', True),
            'user': {
                'first_name': doc.get('user', {}).get('first_name', ''),
                'last_name': doc.get('user', {}).get('last_name', ''),
                'email': doc.get('user', {}).get('email', '')
            } if 'user' in doc else None
        }

class BloodRequestDocument:
    @staticmethod
    def collection():
        return get_db()[Collections.BLOOD_REQUESTS]

    @staticmethod
    def create(data):
        now = datetime.now(timezone.utc)
        document = {
            'patient_id': ObjectId(data['patient_id']),
            'blood_group': data['blood_group'],
            'units_required': int(data.get('units_required', 1)),
            'urgency': data.get('urgency', 'Normal'),
            'hospital_name': data.get('hospital_name', ''),
            'address_line': data.get('address_line', ''),
            'city': data.get('city', '').strip().lower(),
            'state': data.get('state', ''),
            'zip_code': data.get('zip_code', ''),
            'contact_name': data.get('contact_name', ''),
            'contact_phone': data.get('contact_phone', ''),
            'reason': data.get('reason', ''),
            'status': 'Pending',
            'rejection_reason': data.get('rejection_reason',''),
            'created_at': now,
            'updated_at': now,
        }
        result = BloodRequestDocument.collection().insert_one(document)
        document['_id'] = str(result.inserted_id)
        document['patient_id'] = str(document['patient_id'])
        return document

    @staticmethod
    def get_all(blood_group=None, city=None, status='Pending'):
        query = {}
        if status:
            query['status'] = status
        if blood_group:
            query['blood_group'] = blood_group
        if city:
            query['city'] = city.strip().lower()
            
        docs = list(BloodRequestDocument.collection().find(query).sort('created_at', DESCENDING))
        for doc in docs:
            doc['_id'] = str(doc['_id'])
            doc['patient_id'] = str(doc['patient_id'])
        doc['rejection_reason'] = doc.get('rejection_reason', '')
        return docs

    @staticmethod
    def update_status(req_id, status):
        now = datetime.now(timezone.utc)
        result = BloodRequestDocument.collection().update_one(
            {'_id': ObjectId(req_id)},
            {'$set': {'status': status, 'updated_at': now}}
        )
        return result.modified_count > 0

    @staticmethod
    def serialize(doc):
        if not doc:
            return {}
        return {
            'id': str(doc.get('_id', '')),
            'patient_id': str(doc.get('patient_id', '')),
            'blood_group': doc.get('blood_group', ''),
            'units_required': doc.get('units_required', 1),
            'urgency': doc.get('urgency', 'Normal'),
            'hospital_name': doc.get('hospital_name', ''),
            'city': doc.get('city', '').title(),
            'contact_name': doc.get('contact_name', ''),
            'contact_phone': doc.get('contact_phone', ''),
            'reason': doc.get('reason', ''),
            'status': doc.get('status', 'Pending'),
            'rejection_reason': doc.get('rejection_reason',''),
            'created_at': doc['created_at'].isoformat() if doc.get('created_at') else None,
        }
