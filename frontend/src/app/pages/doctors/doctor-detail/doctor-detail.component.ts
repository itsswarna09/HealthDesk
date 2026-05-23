import { Component, inject, OnInit } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../../shared/navbar/navbar.component';
import { DoctorService } from '../../../core/services/doctor.service';
import { AppointmentService } from '../../../core/services/appointment.service';
import { AuthService } from '../../../core/services/auth.service';
import { Doctor } from '../../../core/models/doctor.model';

@Component({
  selector: 'app-doctor-detail',
  standalone: true,
  imports: [CommonModule, NavbarComponent, FormsModule, RouterLink],
  templateUrl: './doctor-detail.component.html',
  styleUrl: './doctor-detail.component.css'
})
export class DoctorDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private location = inject(Location);
  private doctorService = inject(DoctorService);
  private appointmentService = inject(AppointmentService);
  auth = inject(AuthService);

  doctor: Doctor | null = null;
  loading = true;

  // ── Booking Modal State ──
  showBookingModal = false;
  selectedDate = '';
  selectedSlot = '';
  bookingReason = '';
  bookingLoading = false;
  bookingSuccess = false;
  bookingError = '';
  dynamicSlots: string[] = [];
  slotsLoading = false;
  isDayOff = false;

  get isPatient() {
    return this.auth.currentUser()?.role === 'PATIENT';
  }

  get selectedDayName(): string {
    if (!this.selectedDate) return '';
    const [year, month, day] = this.selectedDate.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[d.getDay()];
  }

  get availableSlots(): string[] {
    return this.dynamicSlots;
  }

  get minDate(): string {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.doctorService.getDoctorDetails(id).subscribe({
        next: (res) => {
          if (res.success && res.data) {
            this.doctor = res.data;
          }
          this.loading = false;
        },
        error: () => { this.loading = false; }
      });
    }
  }

  openBooking() {
    // Reset everything for a fresh booking attempt
    this.selectedDate = '';
    this.selectedSlot = '';
    this.bookingReason = '';
    this.bookingError = '';
    this.bookingSuccess = false;
    this.bookingLoading = false;
    this.dynamicSlots = [];
    this.slotsLoading = false;
    this.isDayOff = false;
    this.showBookingModal = true;
  }

  closeBooking() {
    this.showBookingModal = false;
  }

  onDateChange() {
    this.selectedSlot = '';
    this.dynamicSlots = [];
    this.isDayOff = false;
    this.bookingError = '';

    if (!this.selectedDate || !this.doctor) return;

    // Check if it's explicitly an unavailable date
    if (this.doctor.unavailable_dates?.includes(this.selectedDate)) {
      this.isDayOff = true;
      return;
    }

    this.slotsLoading = true;
    this.appointmentService.getAvailableSlots(this.doctor.id, this.selectedDate).subscribe({
      next: (res) => {
        if (res.success && res.data) {
          this.dynamicSlots = res.data;
          if (this.dynamicSlots.length === 0) {
            // Check if the day itself is off (no slots returned)
            this.isDayOff = false; // It might just be fully booked
          }
        }
        this.slotsLoading = false;
      },
      error: () => {
        this.slotsLoading = false;
      }
    });
  }

  selectSlot(slot: string) {
    this.selectedSlot = slot;
    this.bookingError = '';
  }

  confirmBooking() {
    if (!this.selectedSlot || !this.selectedDate || !this.doctor) return;
    this.bookingLoading = true;
    this.bookingError = '';

    this.appointmentService.bookAppointment({
      doctor_id: this.doctor.id,
      date: this.selectedDate,
      time_slot: this.selectedSlot,
      reason_for_visit: this.bookingReason
    }).subscribe({
      next: (res) => {
        this.bookingLoading = false;
        if (res.success) {
          this.bookingSuccess = true;
        } else {
          this.bookingError = res.message || 'Booking failed. Please try again.';
        }
      },
      error: (err) => {
        this.bookingLoading = false;
        const errObj = err.error;
        if (errObj && errObj.errors) {
          const errorList: string[] = [];
          Object.keys(errObj.errors).forEach(key => {
            const val = errObj.errors[key];
            if (Array.isArray(val)) {
              errorList.push(...val);
            } else if (typeof val === 'string') {
              errorList.push(val);
            }
          });
          if (errorList.length > 0) {
            this.bookingError = errorList.join(' ');
            return;
          }
        }
        this.bookingError = errObj?.message || 'Something went wrong. Please try again.';
      }
    });
  }

  goBack() {
    this.location.back();
  }
}
