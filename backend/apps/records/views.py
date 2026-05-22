import os
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.parsers import MultiPartParser, FormParser

from core.utils.api_response import APIResponse
from apps.users.models import Role
from .models import MedicalRecordDocument, RECORD_CATEGORIES


class MedicalRecordListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        role = request.auth.get('role')
        category = request.query_params.get('category')
        
        if role == Role.PATIENT:
            target_patient_id = str(request.user.id)
        elif role == Role.DOCTOR:
            target_patient_id = request.query_params.get('patient_id')
            if not target_patient_id:
                return APIResponse.error('patient_id is required for doctors to view records.', status_code=400)
        else:
            return APIResponse.error('Unauthorized role.', status_code=403)

        records = MedicalRecordDocument.find_by_patient(target_patient_id, category)
        return APIResponse.success(data=[MedicalRecordDocument.serialize(r) for r in records])

    def post(self, request):
        if request.auth.get('role') != Role.PATIENT:
            return APIResponse.error('Only patients can upload records.', status_code=403)

        title = request.data.get('title', '').strip()
        if not title:
            return APIResponse.error('Title is required.')

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return APIResponse.error('A file is required.')

        allowed_types = [
            'application/pdf', 'image/jpeg', 'image/png', 'image/gif',
            'image/webp', 'image/bmp', 'image/tiff',
        ]
        if uploaded_file.content_type not in allowed_types:
            return APIResponse.error('Only PDF and image files are allowed.')

        max_size = 10 * 1024 * 1024  # 10 MB
        if uploaded_file.size > max_size:
            return APIResponse.error('File must be under 10 MB.')

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'medical_records', str(request.user.id))
        os.makedirs(upload_dir, exist_ok=True)

        import uuid
        ext = os.path.splitext(uploaded_file.name)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(upload_dir, unique_name)

        with open(file_path, 'wb+') as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

        relative_path = os.path.join('medical_records', str(request.user.id), unique_name)

        record = MedicalRecordDocument.create({
            'patient_id':  str(request.user.id),
            'title':       title,
            'category':    request.data.get('category', 'Other'),
            'description': request.data.get('description', ''),
            'doctor_name': request.data.get('doctor_name', ''),
            'record_date': request.data.get('record_date', ''),
            'file_name':   uploaded_file.name,
            'file_path':   relative_path,
            'file_size':   uploaded_file.size,
            'file_type':   uploaded_file.content_type,
        })
        return APIResponse.created(data=MedicalRecordDocument.serialize(record), message='Record uploaded successfully.')


class MedicalRecordDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, record_id):
        record = MedicalRecordDocument.find_by_id(record_id)
        if not record:
            return APIResponse.not_found('Record not found.')
            
        role = request.auth.get('role')
        if role == Role.PATIENT and record['patient_id'] != str(request.user.id):
            return APIResponse.error('Not authorized.', status_code=403)
            
        return APIResponse.success(data=MedicalRecordDocument.serialize(record))

    def delete(self, request, record_id):
        record = MedicalRecordDocument.find_by_id(record_id)
        if not record:
            return APIResponse.not_found('Record not found.')
        if record['patient_id'] != str(request.user.id):
            return APIResponse.error('Not authorized.', status_code=403)

        file_full_path = os.path.join(settings.MEDIA_ROOT, record['file_path'])
        if os.path.exists(file_full_path):
            os.remove(file_full_path)

        MedicalRecordDocument.delete(record_id)
        return APIResponse.success(message='Record deleted successfully.')


class MedicalRecordDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, record_id):
        record = MedicalRecordDocument.find_by_id(record_id)
        if not record:
            return APIResponse.not_found('Record not found.')
            
        role = request.auth.get('role')
        if role == Role.PATIENT and record['patient_id'] != str(request.user.id):
            return APIResponse.error('Not authorized.', status_code=403)

        file_full_path = os.path.join(settings.MEDIA_ROOT, record['file_path'])
        if not os.path.exists(file_full_path):
            raise Http404('File not found on server.')

        response = FileResponse(
            open(file_full_path, 'rb'),
            content_type=record.get('file_type', 'application/octet-stream')
        )
        response['Content-Disposition'] = f'attachment; filename="{record["file_name"]}"'
        return response


class RecordCategoriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return APIResponse.success(data=RECORD_CATEGORIES)
