from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from bson import ObjectId

from core.utils.api_response import APIResponse
from core.permissions import IsDoctor, IsPatient
from apps.users.models import Role, UserDocument
from .models import DoctorDocument, AppointmentDocument
from .serializers import DoctorProfileSerializer, AppointmentBookSerializer, AppointmentStatusUpdateSerializer

class DoctorListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        spec = request.query_params.get('specialization')
        query = {'is_verified': True}
        if spec:
            query['specialization'] = spec

        doctors = list(DoctorDocument.collection().find(query))
        data = [DoctorDocument.serialize(doc, include_user=True) for doc in doctors]
        return APIResponse.success(data=data)

class SpecializationListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Fetch highly efficient distinct specializations for verified doctors only
        specializations = DoctorDocument.collection().distinct('specialization', {'is_verified': True})
        # Filter out empty or None values and sort alphabetically
        valid_specs = sorted([s for s in specializations if s])
        return APIResponse.success(data=valid_specs)

class DoctorDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, doctor_id):
        doc = DoctorDocument.find_by_id(doctor_id)
        if not doc:
            return APIResponse.not_found('Doctor not found.')
        return APIResponse.success(data=DoctorDocument.serialize(doc, include_user=True))

class DoctorProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        if request.auth.get('role') != Role.DOCTOR:
            return APIResponse.error('Only doctors can update doctor profiles.', status_code=status.HTTP_403_FORBIDDEN)
            
        doc = DoctorDocument.find_by_user_id(str(request.user.id))
        if not doc:
            doc = DoctorDocument.create(str(request.user.id), {})
            
        serializer = DoctorProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error('Invalid data.', errors=serializer.errors)

        DoctorDocument.update(doc['_id'], serializer.validated_data)
        updated_doc = DoctorDocument.find_by_id(doc['_id'])
        return APIResponse.success(data=DoctorDocument.serialize(updated_doc), message='Doctor profile updated successfully.')

class AppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.auth.get('role')
        if role == Role.PATIENT:
            appointments = list(AppointmentDocument.collection().find({'patient_id': ObjectId(request.user.id)}))
        elif role == Role.DOCTOR:
            doctor = DoctorDocument.find_by_user_id(str(request.user.id))
            if not doctor:
                return APIResponse.success(data=[])
            appointments = list(AppointmentDocument.collection().find({'doctor_id': ObjectId(doctor['_id'])}))
        else:
            appointments = []
            
        data = [AppointmentDocument.serialize(a, include_relations=True) for a in appointments]
        return APIResponse.success(data=data)

    def post(self, request):
        if request.auth.get('role') != Role.PATIENT:
            return APIResponse.error('Only patients can book appointments.', status_code=status.HTTP_403_FORBIDDEN)
            
        serializer = AppointmentBookSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error('Invalid booking data.', errors=serializer.errors)

        data = serializer.validated_data
        data['patient_id'] = str(request.user.id)
        
        appointment = AppointmentDocument.create(data)
        return APIResponse.created(data=AppointmentDocument.serialize(appointment), message='Appointment booked successfully.')

class AppointmentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, app_id):
        if request.auth.get('role') != Role.DOCTOR:
            return APIResponse.error('Only doctors can update statuses.', status_code=status.HTTP_403_FORBIDDEN)
            
        serializer = AppointmentStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error('Invalid status data.', errors=serializer.errors)

        appointment = AppointmentDocument.find_by_id(app_id)
        if not appointment:
            return APIResponse.not_found('Appointment not found.')

        doctor = DoctorDocument.find_by_user_id(str(request.user.id))
        if not doctor or appointment.get('doctor_id') != doctor['_id']:
            return APIResponse.error('Not authorized to update this appointment.', status_code=status.HTTP_403_FORBIDDEN)

        status_str = serializer.validated_data['status']
        AppointmentDocument.update_status(app_id, status_str)
        
        notes = serializer.validated_data.get('notes')
        if notes:
            AppointmentDocument.collection().update_one(
                {'_id': ObjectId(app_id)},
                {'$set': {'notes': notes}}
            )

        updated = AppointmentDocument.find_by_id(app_id)
        return APIResponse.success(data=AppointmentDocument.serialize(updated), message=f'Appointment marked as {status_str}.')

class AppointmentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, app_id):
        appointment = AppointmentDocument.find_by_id(app_id)
        if not appointment:
            return APIResponse.not_found('Appointment not found.')

        role = request.auth.get('role')
        # Security: only the owning patient or the assigned doctor can view
        if role == Role.PATIENT and appointment.get('patient_id') != str(request.user.id):
            return APIResponse.error('Not authorized.', status_code=status.HTTP_403_FORBIDDEN)
        if role == Role.DOCTOR:
            doctor = DoctorDocument.find_by_user_id(str(request.user.id))
            if not doctor or str(appointment.get('doctor_id')) != str(doctor['_id']):
                return APIResponse.error('Not authorized.', status_code=status.HTTP_403_FORBIDDEN)

        return APIResponse.success(data=AppointmentDocument.serialize(appointment, include_relations=True))


class AppointmentCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, app_id):
        if request.auth.get('role') != Role.PATIENT:
            return APIResponse.error('Only patients can cancel appointments.', status_code=status.HTTP_403_FORBIDDEN)

        appointment = AppointmentDocument.find_by_id(app_id)
        if not appointment:
            return APIResponse.not_found('Appointment not found.')

        if str(appointment.get('patient_id')) != str(request.user.id):
            return APIResponse.error('Not authorized to cancel this appointment.', status_code=status.HTTP_403_FORBIDDEN)

        if appointment.get('status') in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
            return APIResponse.error('Cannot cancel a completed or already cancelled appointment.')

        AppointmentDocument.update_status(app_id, AppointmentStatus.CANCELLED)
        updated = AppointmentDocument.find_by_id(app_id)
        return APIResponse.success(data=AppointmentDocument.serialize(updated), message='Appointment cancelled successfully.')

class DoctorAvailabilityUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        if request.auth.get('role') != Role.DOCTOR:
            return APIResponse.error('Only doctors can update availability.', status_code=status.HTTP_403_FORBIDDEN)
            
        doc = DoctorDocument.find_by_user_id(str(request.user.id))
        if not doc:
            return APIResponse.error('Doctor profile not found.', status_code=status.HTTP_404_NOT_FOUND)
            
        schedule = request.data.get('schedule', {})
        unavailable_dates = request.data.get('unavailable_dates', [])
        
        # basic validation: end > start
        for day, data in schedule.items():
            if data.get('enabled'):
                if data.get('start', '00:00') >= data.get('end', '23:59'):
                    return APIResponse.error(f'Invalid time range for {day}.', status_code=status.HTTP_400_BAD_REQUEST)
                    
        DoctorDocument.update(doc['_id'], {
            'schedule': schedule,
            'unavailable_dates': unavailable_dates
        })
        
        updated_doc = DoctorDocument.find_by_id(doc['_id'])
        return APIResponse.success(data=DoctorDocument.serialize(updated_doc), message='Availability updated successfully.')

class DoctorSlotsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, doctor_id):
        date_str = request.query_params.get('date')
        if not date_str:
            return APIResponse.error('Date parameter is required.')
            
        doctor = DoctorDocument.find_by_id(doctor_id)
        if not doctor:
            return APIResponse.not_found('Doctor not found.')
            
        from datetime import datetime, timezone, timedelta
        
        try:
            req_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            today = datetime.now(timezone.utc).date()
            if req_date < today:
                return APIResponse.success(data=[])
        except ValueError:
            return APIResponse.error('Invalid date format.')
            
        unavailable = doctor.get('unavailable_dates', [])
        if date_str in unavailable:
            return APIResponse.success(data=[])
            
        weekday_name = req_date.strftime('%A').lower()
        schedule = doctor.get('schedule', {})
        day_schedule = schedule.get(weekday_name, {})
        
        if not day_schedule.get('enabled', False):
            return APIResponse.success(data=[])
            
        start_time_str = day_schedule.get('start', '00:00')
        end_time_str = day_schedule.get('end', '23:59')
        
        # Generate 30-min slots
        slots = []
        try:
            start_dt = datetime.strptime(start_time_str, '%H:%M')
            end_dt = datetime.strptime(end_time_str, '%H:%M')
            curr_dt = start_dt
            
            # If date is today, filter out past times
            now = datetime.now(timezone.utc)
            is_today = (req_date == today)
            
            while curr_dt < end_dt:
                slot_str = curr_dt.strftime('%H:%M')
                
                # Check if it's past today
                if is_today:
                    slot_hour, slot_minute = map(int, slot_str.split(':'))
                    if slot_hour < now.hour or (slot_hour == now.hour and slot_minute <= now.minute):
                        curr_dt += timedelta(minutes=30)
                        continue
                        
                slots.append(slot_str)
                curr_dt += timedelta(minutes=30)
        except ValueError:
            pass # Invalid time format
            
        # Remove booked slots
        existing = AppointmentDocument.collection().find({
            'doctor_id': doctor.get('_id'),
            'date': date_str,
            'status': {'$in': [AppointmentStatus.PENDING, AppointmentStatus.ACCEPTED]}
        })
        booked_slots = [doc['time_slot'] for doc in existing]
        
        available_slots = [slot for slot in slots if slot not in booked_slots]
        
        return APIResponse.success(data=available_slots)

