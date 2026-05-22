from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from pymongo import IndexModel, ASCENDING
from bson import ObjectId

from core.db import get_db, Collections
from apps.users.models import UserDocument

class DoctorDocument:
    @staticmethod
    def collection():
        return get_db()[Collections.DOCTORS]

    @staticmethod
    def ensure_indexes():
        collection = DoctorDocument.collection()
        collection.create_indexes([
            IndexModel([('user_id', ASCENDING)], unique=True, name='user_id_unique'),
            IndexModel([('specialization', ASCENDING)], name='specialization_index'),
            IndexModel([('is_verified', ASCENDING)], name='is_verified_index'),
        ])

    @staticmethod
    def create(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        document = {
            'user_id': ObjectId(user_id),
            'specialization': data.get('specialization', 'General Practitioner'),
            'experience_years': data.get('experience_years', 0),
            'qualifications': data.get('qualifications', []),
            'schedule': data.get('schedule', {
                'monday': {'enabled': True, 'start': '09:00', 'end': '17:00'},
                'tuesday': {'enabled': True, 'start': '09:00', 'end': '17:00'},
                'wednesday': {'enabled': True, 'start': '09:00', 'end': '17:00'},
                'thursday': {'enabled': True, 'start': '09:00', 'end': '17:00'},
                'friday': {'enabled': True, 'start': '09:00', 'end': '17:00'},
                'saturday': {'enabled': False, 'start': '09:00', 'end': '13:00'},
                'sunday': {'enabled': False, 'start': '', 'end': ''},
            }),
            'unavailable_dates': data.get('unavailable_dates', []),
            'consultation_fee': data.get('consultation_fee', 0.0),
            'is_verified': False,
            'created_at': now,
            'updated_at': now,
        }
        result = DoctorDocument.collection().insert_one(document)
        document['_id'] = str(result.inserted_id)
        document['user_id'] = str(document['user_id'])
        return document

    @staticmethod
    def find_by_id(doctor_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = DoctorDocument.collection().find_one({'_id': ObjectId(doctor_id)})
            if doc:
                doc['_id'] = str(doc['_id'])
                doc['user_id'] = str(doc['user_id'])
            return doc
        except Exception:
            return None

    @staticmethod
    def find_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = DoctorDocument.collection().find_one({'user_id': ObjectId(user_id)})
            if doc:
                doc['_id'] = str(doc['_id'])
                doc['user_id'] = str(doc['user_id'])
            return doc
        except Exception:
            return None

    @staticmethod
    def update(doctor_id: str, data: Dict[str, Any]) -> bool:
        data['updated_at'] = datetime.now(timezone.utc)
        result = DoctorDocument.collection().update_one(
            {'_id': ObjectId(doctor_id)},
            {'$set': data}
        )
        return result.modified_count > 0

    @staticmethod
    def serialize(doc: Dict[str, Any], include_user: bool = False) -> Dict[str, Any]:
        if not doc:
            return {}
        
        serialized = {
            'id': str(doc.get('_id', '')),
            'user_id': str(doc.get('user_id', '')),
            'specialization': doc.get('specialization', ''),
            'experience_years': doc.get('experience_years', 0),
            'qualifications': doc.get('qualifications', []),
            'schedule': doc.get('schedule', {}),
            'unavailable_dates': doc.get('unavailable_dates', []),
            'consultation_fee': doc.get('consultation_fee', 0.0),
            'is_verified': doc.get('is_verified', False),
        }

        if include_user and doc.get('user_id'):
            user_doc = UserDocument.find_by_id(str(doc['user_id']))
            if user_doc:
                serialized['user'] = UserDocument.serialize(user_doc)
        
        return serialized


class AppointmentStatus:
    PENDING = 'PENDING'
    ACCEPTED = 'ACCEPTED'
    REJECTED = 'REJECTED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    ALL = [PENDING, ACCEPTED, REJECTED, COMPLETED, CANCELLED]


class AppointmentDocument:
    @staticmethod
    def collection():
        return get_db()[Collections.APPOINTMENTS]

    @staticmethod
    def ensure_indexes():
        collection = AppointmentDocument.collection()
        collection.create_indexes([
            IndexModel([('patient_id', ASCENDING)], name='patient_id_index'),
            IndexModel([('doctor_id', ASCENDING)], name='doctor_id_index'),
            IndexModel([('date', ASCENDING), ('time_slot', ASCENDING)], name='datetime_index'),
            IndexModel([('status', ASCENDING)], name='status_index'),
        ])

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        document = {
            'patient_id': ObjectId(data['patient_id']),
            'doctor_id': ObjectId(data['doctor_id']),
            'date': data['date'],
            'time_slot': data['time_slot'],
            'status': AppointmentStatus.PENDING,
            'reason_for_visit': data.get('reason_for_visit', ''),
            'notes': data.get('notes', ''),
            'created_at': now,
            'updated_at': now,
        }
        result = AppointmentDocument.collection().insert_one(document)
        document['_id'] = str(result.inserted_id)
        document['patient_id'] = str(document['patient_id'])
        document['doctor_id'] = str(document['doctor_id'])
        return document

    @staticmethod
    def find_by_id(appointment_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = AppointmentDocument.collection().find_one({'_id': ObjectId(appointment_id)})
            if doc:
                doc['_id'] = str(doc['_id'])
                doc['patient_id'] = str(doc['patient_id'])
                doc['doctor_id'] = str(doc['doctor_id'])
            return doc
        except Exception:
            return None

    @staticmethod
    def update_status(appointment_id: str, status: str) -> bool:
        result = AppointmentDocument.collection().update_one(
            {'_id': ObjectId(appointment_id)},
            {'$set': {'status': status, 'updated_at': datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0

    @staticmethod
    def serialize(doc: Dict[str, Any], include_relations: bool = False) -> Dict[str, Any]:
        if not doc:
            return {}
        
        serialized = {
            'id': str(doc.get('_id', '')),
            'patient_id': str(doc.get('patient_id', '')),
            'doctor_id': str(doc.get('doctor_id', '')),
            'date': doc.get('date', ''),
            'time_slot': doc.get('time_slot', ''),
            'status': doc.get('status', AppointmentStatus.PENDING),
            'reason_for_visit': doc.get('reason_for_visit', ''),
            'notes': doc.get('notes', ''),
            'created_at': doc['created_at'].isoformat() if doc.get('created_at') else None,
        }

        if include_relations:
            patient_doc = UserDocument.find_by_id(str(doc.get('patient_id')))
            if patient_doc:
                serialized['patient'] = UserDocument.serialize(patient_doc)
            
            doctor_doc = DoctorDocument.find_by_id(str(doc.get('doctor_id')))
            if doctor_doc:
                serialized['doctor'] = DoctorDocument.serialize(doctor_doc, include_user=True)

        return serialized
