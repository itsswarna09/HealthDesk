import { Component, inject, OnInit, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../shared/navbar/navbar.component';
import { BloodService, BloodDonor, BloodRequest } from '../../core/services/blood.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-blood-donation',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  templateUrl: './blood-donation.component.html',
  styleUrl: './blood-donation.component.css'
})
export class BloodDonationComponent implements OnInit, AfterViewInit {
  bloodService = inject(BloodService);
  auth = inject(AuthService);

  activeTab: 'requests' | 'donors' | 'my_profile' = 'requests';

  bloodGroups: string[] = [];
  urgencyLevels: string[] = [];

  // Data
  requests: BloodRequest[] = [];
  donors: BloodDonor[] = [];
  myDonorProfile: BloodDonor | null = null;

  @ViewChild('cityInput') cityInput!: ElementRef;
  @ViewChild('stateInput') stateInput!: ElementRef;
  @ViewChild('addressInput') addressInput!: ElementRef;
  filterBloodGroup = '';
  isDoctor = false;
  // UI state for rejection
  showRejectModal = false;
  rejectRequestId = '';
  rejectionReason = '';


  loading = true;

  // Modals
  showRequestModal = false;
  showDonorModal = false;

  requestForm = {
    blood_group: '',
    units_required: 1,
    urgency: 'Normal',
    hospital_name: '',
    address_line: '',
    city: '',
    state: '',
    zip_code: '',
    contact_name: '',
    contact_phone: '',
    reason: ''
  };

  donorForm = {
    blood_group: '',
    city: '',
    phone: '',
    last_donated_date: '',
    is_available: true
  };

  actionLoading = false;
  actionError = '';
  actionSuccess = '';
  editingRequestId: string | null = null; // holds request id when editing

  // Update request status (doctor)
  updateStatus(reqId: string, status: string) {
    const payload: any = { status };
    if (status === 'Rejected') {
      // rejection reason will be set via separate call
      return;
    }
    this.bloodService.updateRequest(reqId, payload).subscribe(res => {
      if (res.success) {
        this.loadData();
      } else {
        this.actionError = res.message || 'Failed to update status.';
      }
    });
  }

  openRejectModal(reqId: string) {
    this.rejectRequestId = reqId;
    this.rejectionReason = '';
    this.showRejectModal = true;
    this.actionError = '';
  }

  closeRejectModal() {
    this.showRejectModal = false;
    this.rejectRequestId = '';
  }

  confirmReject() {
    if (!this.rejectionReason.trim()) {
      this.actionError = 'Rejection reason is required.';
      return;
    }
    const payload = { status: 'Rejected', rejection_reason: this.rejectionReason };
    this.bloodService.updateRequest(this.rejectRequestId, payload).subscribe(res => {
      if (res.success) {
        this.loadData();
        this.closeRejectModal();
      } else {
        this.actionError = res.message || 'Failed to reject.';
      }
    });
  }
    // Initialize Google Places Autocomplete for address fields if the API is loaded
    if ((window as any).google && (window as any).google.maps && (window as any).google.maps.places) {
      const addressAutocomplete = new (window as any).google.maps.places.Autocomplete(this.addressInput.nativeElement, { types: ['address'] });
      const cityAutocomplete = new (window as any).google.maps.places.Autocomplete(this.cityInput.nativeElement, { types: ['(cities)'] });
      const stateAutocomplete = new (window as any).google.maps.places.Autocomplete(this.stateInput.nativeElement, { types: ['(regions)'] });
      addressAutocomplete.addListener('place_changed', () => {
        const place = addressAutocomplete.getPlace();
        this.requestForm.address_line = place.formatted_address || '';
      });
      cityAutocomplete.addListener('place_changed', () => {
        const place = cityAutocomplete.getPlace();
        this.requestForm.city = place.name || '';
      });
      stateAutocomplete.addListener('place_changed', () => {
        const place = stateAutocomplete.getPlace();
        this.requestForm.state = place.name || '';
      });
    }
  }

    // Determine if user is doctor on init
    this.isDoctor = this.auth.currentUser()?.role === 'DOCTOR';

      if (res.success && res.data) {
        this.bloodGroups = res.data.blood_groups;
        this.urgencyLevels = res.data.urgency_levels;
      }
      this.loadData();
    });
  }

  loadData() {
    this.loading = true;
    if (this.activeTab === 'requests') {
      // Build optional status filter for doctors
      const statusParam = this.filterStatus ? this.filterStatus : undefined;
      this.bloodService.getRequests(this.filterBloodGroup, this.filterCity, statusParam).subscribe(res => {
        if (res.success) this.requests = res.data || [];
        this.loading = false;
      });
    } else if (this.activeTab === 'donors') {
      this.bloodService.getDonors(this.filterBloodGroup, this.filterCity).subscribe(res => {
        if (res.success) this.donors = res.data || [];
        this.loading = false;
      });
    } else if (this.activeTab === 'my_profile') {
      this.bloodService.getMyDonorProfile().subscribe(res => {
        if (res.success) {
          this.myDonorProfile = res.data || null;
          if (this.myDonorProfile) {
            this.donorForm = {
              blood_group: this.myDonorProfile.blood_group,
              city: this.myDonorProfile.city,
              phone: this.myDonorProfile.phone,
              last_donated_date: this.myDonorProfile.last_donated_date || '',
              is_available: this.myDonorProfile.is_available
            };
          }
        }
        this.loading = false;
      });
    }
  }

  switchTab(tab: 'requests' | 'donors' | 'my_profile') {
    this.activeTab = tab;
    this.filterBloodGroup = '';
    this.filterCity = '';
    this.loadData();
  }

  applyFilters() {
    this.loadData();
  }

  // Request Modal
  openRequestModal() {
    this.editingRequestId = null;
    this.showRequestModal = true;
    this.actionError = '';
    this.requestForm = { blood_group: this.bloodGroups[0] || '', units_required: 1, urgency: 'Normal', hospital_name: '', address_line: '', city: '', state: '', zip_code: '', contact_name: '', contact_phone: '', reason: '' };
  }

  // Open modal for editing an existing pending request
  openEditRequestModal(req: BloodRequest) {
    this.editingRequestId = req.id;
    this.showRequestModal = true;
    this.actionError = '';
    this.requestForm = {
      blood_group: req.blood_group,
      units_required: req.units_required,
      urgency: req.urgency,
      hospital_name: req.hospital_name,
      address_line: req.address_line || '',
      city: req.city,
      state: req.state || '',
      zip_code: req.zip_code || '',
      contact_name: req.contact_name,
      contact_phone: req.contact_phone,
      reason: req.reason || ''
    };
  }
  closeRequestModal() { this.showRequestModal = false; }

  submitRequest() {
    if (!this.requestForm.blood_group || !this.requestForm.hospital_name || !this.requestForm.address_line || !this.requestForm.city || !this.requestForm.state || !this.requestForm.zip_code || !this.requestForm.contact_name || !this.requestForm.contact_phone) {
      this.actionError = 'Please fill all required fields.';
      return;
    }
    this.actionLoading = true;
    if (this.editingRequestId) {
      // Update existing request
      this.bloodService.updateRequest(this.editingRequestId, this.requestForm).subscribe({
        next: (res) => {
          this.actionLoading = false;
          if (res.success) {
            this.closeRequestModal();
            this.editingRequestId = null;
            this.loadData();
            this.actionSuccess = 'Request updated successfully!';
            setTimeout(() => this.actionSuccess = '', 4000);
          } else {
            this.actionError = res.message || 'Failed to update request.';
          }
        },
        error: (err) => {
          this.actionLoading = false;
          this.actionError = err.error?.message || 'Server error occurred.';
        }
      });
    } else {
      // Create new request
      this.bloodService.createRequest(this.requestForm).subscribe({
        next: (res) => {
          this.actionLoading = false;
          if (res.success) {
            this.closeRequestModal();
            this.loadData();
            this.actionSuccess = 'Blood request posted successfully!';
            setTimeout(() => this.actionSuccess = '', 4000);
          } else {
            this.actionError = res.message || 'Failed to post request.';
          }
        },
        error: (err) => {
          this.actionLoading = false;
          this.actionError = err.error?.message || 'Server error occurred.';
        }
      });
    }
  }

  // Donor Modal
  openDonorModal() {
    this.showDonorModal = true;
    this.actionError = '';
    if (!this.myDonorProfile) {
      this.donorForm.blood_group = this.bloodGroups[0] || '';
    }
  }
  closeDonorModal() { this.showDonorModal = false; }

  submitDonor() {
    if (!this.donorForm.blood_group || !this.donorForm.city || !this.donorForm.phone) {
      this.actionError = 'Please fill all required fields.';
      return;
    }
    this.actionLoading = true;
    this.bloodService.registerAsDonor(this.donorForm).subscribe({
      next: (res) => {
        this.actionLoading = false;
        if (res.success) {
          this.closeDonorModal();
          this.loadData(); // Will reload profile
          this.actionSuccess = 'Donor profile updated successfully!';
          setTimeout(() => this.actionSuccess = '', 4000);
        } else {
          this.actionError = res.message || 'Failed to update donor profile.';
        }
      },
      error: (err) => {
        this.actionLoading = false;
        this.actionError = err.error?.message || 'Server error occurred.';
      }
    });
  }

  markFulfilled(id: string) {
    if (confirm('Mark this request as fulfilled?')) {
      this.bloodService.updateRequestStatus(id, 'Fulfilled').subscribe(res => {
        if (res.success) this.loadData();
      });
    }
  }

  getUrgencyColor(urgency: string) {
    if (urgency === 'Emergency') return 'urgency-emergency';
    if (urgency === 'Urgent') return 'urgency-urgent';
    return 'urgency-normal';
  }
}
