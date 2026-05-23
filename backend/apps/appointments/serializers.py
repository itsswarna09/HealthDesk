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
            
        from datetime import datetime, timedelta
        from django.utils import timezone as django_timezone
        
        # Parse full requested slot datetime
        try:
            req_date = datetime.strptime(date, '%Y-%m-%d').date()
            req_dt = datetime.strptime(f"{date} {time_slot}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise serializers.ValidationError("Invalid date or time slot format.")
            
        # Get timezone-aware current time and set req_dt to active timezone
        now = django_timezone.now()
        current_timezone = django_timezone.get_current_timezone()
        req_dt = django_timezone.make_aware(req_dt, current_timezone)
        
        # 1. Prevent booking in the past (date or time)
        if req_dt < now:
            raise serializers.ValidationError("Cannot book appointments in the past.")
            
        # 2. Minimum booking window (15 minutes from now)
        min_booking_time = now + timedelta(minutes=15)
        if req_dt < min_booking_time:
            raise serializers.ValidationError("Appointments must be booked at least 15 minutes in advance.")
            
        # 3. Enforce 30-minute boundary
        if req_dt.minute not in [0, 30]:
            raise serializers.ValidationError("Appointments can only be booked in 30-minute increments (e.g. HH:00 or HH:30).")
            
        # 4. Check unavailable dates
        unavailable = doctor.get('unavailable_dates', [])
        if date in unavailable:
            raise serializers.ValidationError("Doctor is not available on this date.")
            
        # 5. Check working hours and day
        weekday_name = req_date.strftime('%A').lower()
        schedule = doctor.get('schedule', {})
        day_schedule = schedule.get(weekday_name, {})
        
        if not day_schedule.get('enabled', False):
            raise serializers.ValidationError(f"Doctor is not available on {weekday_name.capitalize()}s.")
            
        start = day_schedule.get('start', '00:00')
        end = day_schedule.get('end', '23:59')
        if not (start <= time_slot < end):
            raise serializers.ValidationError(f"Time slot must be within doctor's working hours ({start} - {end}).")
            
        # 6. Ensure slot isn't already booked
        from bson import ObjectId
        existing = AppointmentDocument.collection().find_one({
            'doctor_id': ObjectId(doctor.get('_id')),
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
