from datetime import datetime, timezone
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
from core.db import get_db, Collections


RECORD_CATEGORIES = [
    'Prescription', 'Blood Test', 'Scan / X-Ray', 'MRI',
    'Vaccination', 'Lab Report', 'Discharge Summary', 'Other'
]


class MedicalRecordDocument:
    @staticmethod
    def collection():
        return get_db()[Collections.MEDICAL_RECORDS]

    @staticmethod
    def create(data):
        now = datetime.now(timezone.utc)
        document = {
            'patient_id': ObjectId(data['patient_id']),
            'title': data['title'],
            'category': data.get('category', 'Other'),
            'description': data.get('description', ''),
            'doctor_name': data.get('doctor_name', ''),
            'record_date': data.get('record_date', ''),
            'file_name': data['file_name'],
            'file_path': data['file_path'],
            'file_size': data.get('file_size', 0),
            'file_type': data.get('file_type', ''),
            'created_at': now,
            'updated_at': now,
        }
        result = MedicalRecordDocument.collection().insert_one(document)
        document['_id'] = str(result.inserted_id)
        document['patient_id'] = str(document['patient_id'])
        return document

    @staticmethod
    def find_by_id(record_id):
        try:
            doc = MedicalRecordDocument.collection().find_one({'_id': ObjectId(record_id)})
            if doc:
                doc['_id'] = str(doc['_id'])
                doc['patient_id'] = str(doc['patient_id'])
            return doc
        except Exception:
            return None

    @staticmethod
    def find_by_patient(patient_id, category=None):
        query = {'patient_id': ObjectId(patient_id)}
        if category:
            query['category'] = category
        docs = list(MedicalRecordDocument.collection().find(query).sort('created_at', DESCENDING))
        for doc in docs:
            doc['_id'] = str(doc['_id'])
            doc['patient_id'] = str(doc['patient_id'])
        return docs

    @staticmethod
    def delete(record_id):
        result = MedicalRecordDocument.collection().delete_one({'_id': ObjectId(record_id)})
        return result.deleted_count > 0

    @staticmethod
    def serialize(doc):
        if not doc:
            return {}
        return {
            'id': str(doc.get('_id', '')),
            'patient_id': str(doc.get('patient_id', '')),
            'title': doc.get('title', ''),
            'category': doc.get('category', ''),
            'description': doc.get('description', ''),
            'doctor_name': doc.get('doctor_name', ''),
            'record_date': doc.get('record_date', ''),
            'file_name': doc.get('file_name', ''),
            'file_size': doc.get('file_size', 0),
            'file_type': doc.get('file_type', ''),
            'created_at': doc['created_at'].isoformat() if doc.get('created_at') else None,
        }
