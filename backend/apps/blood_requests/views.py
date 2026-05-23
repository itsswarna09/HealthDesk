from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.utils.api_response import APIResponse
from .models import BloodDonorDocument, BloodRequestDocument, BLOOD_GROUPS, URGENCY_LEVELS

class BloodDonorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doc = BloodDonorDocument.find_by_user(str(request.user.id))
        return APIResponse.success(data=BloodDonorDocument.serialize(doc) if doc else None)

    def post(self, request):
        data = request.data
        if not data.get('blood_group') or data.get('blood_group') not in BLOOD_GROUPS:
            return APIResponse.error('Valid blood group is required.')
        if not data.get('city'):
            return APIResponse.error('City is required.')
        if not data.get('phone'):
            return APIResponse.error('Phone number is required.')

        doc = BloodDonorDocument.register(str(request.user.id), data)
        return APIResponse.success(data=BloodDonorDocument.serialize(doc), message='Registered as donor successfully.')

class BloodDonorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        blood_group = request.query_params.get('blood_group')
        city = request.query_params.get('city')
        donors = BloodDonorDocument.get_donors(blood_group, city)
        return APIResponse.success(data=[BloodDonorDocument.serialize(d) for d in donors])

class BloodRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        blood_group = request.query_params.get('blood_group')
        city = request.query_params.get('city')
        # Allow doctors to view all requests, patients default to pending only
        user_role = getattr(request.user, 'role', None)
        if user_role == 'DOCTOR':
            status = request.query_params.get('status')  # doctors can filter any status
        else:
            status = request.query_params.get('status', 'Pending')
        reqs = BloodRequestDocument.get_all(blood_group, city, status)
        return APIResponse.success(data=[BloodRequestDocument.serialize(r) for r in reqs])

    def post(self, request):
        data = request.data
        if not data.get('blood_group') or data.get('blood_group') not in BLOOD_GROUPS:
            return APIResponse.error('Valid blood group is required.')
        # Ensure all address related fields are present
        required = ['hospital_name', 'address_line', 'city', 'state', 'zip_code', 'contact_name', 'contact_phone']
        if any(not data.get(f) for f in required):
            return APIResponse.error('Hospital name, address, city, state, zip code, contact name, and phone are required.')
        data['patient_id'] = str(request.user.id)
        doc = BloodRequestDocument.create(data)
        return APIResponse.created(data=BloodRequestDocument.serialize(doc), message='Blood request created.')

class BloodRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, req_id):
        # Determine if this is a status change (doctor) or full edit (patient)
        user = request.user
        data = request.data
        # Doctor actions: only allow status change to Accepted/Rejected/Fulfilled/Closed
        if getattr(user, 'role', None) == 'DOCTOR':
            # Doctors can change status and optionally provide a rejection reason
            status = data.get('status')
            if not status or status not in STATUS_CHOICES:
                return APIResponse.error('Valid status is required.')
            update_fields = {'status': status, 'updated_at': datetime.now(timezone.utc)}
            if status == 'Rejected' and data.get('rejection_reason'):
                update_fields['rejection_reason'] = data.get('rejection_reason')
            result = BloodRequestDocument.collection().update_one(
                {'_id': ObjectId(req_id)},
                {'$set': update_fields}
            )
            if result.modified_count > 0:
                return APIResponse.success(message='Request status updated.')
            return APIResponse.error('Failed to update status.')
        # Patient actions: allow edit only if request is still Pending and belongs to them
        req = BloodRequestDocument.collection().find_one({'_id': ObjectId(req_id)})
        if not req:
            return APIResponse.error('Request not found.')
        if str(req.get('patient_id')) != str(user.id):
            return APIResponse.error('Permission denied.')
        if req.get('status') != 'Pending':
            return APIResponse.error('Cannot edit a request that is already processed.')
        # Allowed fields for edit (same as creation except status)
        allowed = ['blood_group', 'units_required', 'urgency', 'hospital_name', 'address_line', 'city', 'state', 'zip_code', 'contact_name', 'contact_phone', 'reason']
        update_doc = {k: data[k] for k in allowed if k in data}
        if not update_doc:
            return APIResponse.error('No editable fields provided.')
        update_doc['updated_at'] = datetime.now(timezone.utc)
        result = BloodRequestDocument.collection().update_one({'_id': ObjectId(req_id)}, {'$set': update_doc})
        if result.modified_count > 0:
            return APIResponse.success(message='Request edited successfully.')
        return APIResponse.error('Failed to edit request.')

class BloodOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return APIResponse.success(data={
            'blood_groups': BLOOD_GROUPS,
            'urgency_levels': URGENCY_LEVELS
        })
