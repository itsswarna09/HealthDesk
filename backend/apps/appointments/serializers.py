from rest_framework import serializers
from .models import DoctorDocument, AppointmentDocument, AppointmentStatus

class DoctorProfileSerializer(serializers.Serializer):
    specialization = serializers.CharField(max_length=100, required=False)
    experience_years = serializers.IntegerField(min_value=0, required=False)
    consultation_fee = serializers.FloatField(min_value=0.0, required=False)
    # Lists of strings and dicts are harder in simple serializers, but possible using JSON fields
    # Here we use basic fields, for availability and qualifications we accept lists
    qualifications = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False
    )
    schedule = serializers.DictField(required=False)
    unavailable_dates = serializers.ListField(
        child=serializers.CharField(max_length=10), required=False
    )

class AppointmentBookSerializer(serializers.Serializer):
    doctor_id = serializers.CharField(max_length=24, required=True)
    date = serializers.CharField(max_length=10, required=True) # YYYY-MM-DD
    time_slot = serializers.CharField(max_length=5, required=True) # HH:MM
    reason_for_visit = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        doctor_id = attrs['doctor_id']
        date = attrs['date']
        time_slot = attrs['time_slot']
        
        # Ensure doctor exists
        doctor = DoctorDocument.find_by_id(doctor_id)
        if not doctor:
            raise serializers.ValidationError("Doctor not found.")
            
        from datetime import datetime, timezone
        
        # Check past date
        try:
            req_date = datetime.strptime(date, '%Y-%m-%d').date()
            today = datetime.now(timezone.utc).date()
            if req_date < today:
                raise serializers.ValidationError("Cannot book appointments in the past.")
        except ValueError:
            raise serializers.ValidationError("Invalid date format.")
            
        # Check unavailable dates
        unavailable = doctor.get('unavailable_dates', [])
        if date in unavailable:
            raise serializers.ValidationError("Doctor is not available on this date.")
            
        # Check working hours and day
        weekday_name = req_date.strftime('%A').lower()
        schedule = doctor.get('schedule', {})
        day_schedule = schedule.get(weekday_name, {})
        
        if not day_schedule.get('enabled', False):
            raise serializers.ValidationError(f"Doctor is not available on {weekday_name.capitalize()}s.")
            
        start = day_schedule.get('start', '00:00')
        end = day_schedule.get('end', '23:59')
        if not (start <= time_slot < end):
            raise serializers.ValidationError(f"Time slot must be within doctor's working hours ({start} - {end}).")
        
        # Ensure doctor is available on this day/time
        # Simplified validation for MVP: we just check if it's already booked
        existing = AppointmentDocument.collection().find_one({
            'doctor_id': doctor.get('_id'),
            'date': date,
            'time_slot': time_slot,
            'status': {'$in': [AppointmentStatus.PENDING, AppointmentStatus.ACCEPTED]}
        })
        if existing:
            raise serializers.ValidationError("This time slot is already booked.")
            
        return attrs

class AppointmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[(s, s) for s in AppointmentStatus.ALL])
    notes = serializers.CharField(required=False, allow_blank=True)
