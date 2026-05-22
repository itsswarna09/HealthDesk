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

  // ── Booking Modal ──────────────────────────────────────────────
  showBookingModal = false;
  selectedDate: string = '';
  selectedSlot: string = '';
  bookingReason: string = '';
  bookingLoading = false;
  bookingSuccess = false;
  bookingError = '';

  get isPatient() {
    return this.auth.currentUser()?.role === 'PATIENT';
  }

  get selectedDayName(): string {
    if (!this.selectedDate) return '';
    // Must parse as local date to get correct day
    const [year, month, day] = this.selectedDate.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[d.getDay()];
  }

  dynamicSlots: string[] = [];
  slotsLoading = false;
  isDayOff = false;

  get availableSlots(): string[] {
    return this.dynamicSlots;
  }

  get minDate(): string {
    return new Date().toISOString().split('T')[0];
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
    this.showBookingModal = true;
    this.bookingSuccess = false;
    this.bookingError = '';
    // Keep selectedDate and selectedSlot as they are for the modal
    this.bookingReason = '';
  }

  closeBooking() {
    this.showBookingModal = false;
  }

  onDateChange() {
    this.selectedSlot = '';
    this.dynamicSlots = [];
    this.isDayOff = false;

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
        if (res.success) {
          this.bookingSuccess = true;
        } else {
          this.bookingError = res.message || 'Booking failed. Please try again.';
        }
        this.bookingLoading = false;
      },
      error: (err) => {
        this.bookingError = err.error?.message || 'Something went wrong. Please try again.';
        this.bookingLoading = false;
      }
    });
  }

  goBack() {
    this.location.back();
  }
}
