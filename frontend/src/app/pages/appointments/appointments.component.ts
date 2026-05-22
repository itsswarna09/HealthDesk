import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../shared/navbar/navbar.component';
import { AppointmentService } from '../../core/services/appointment.service';
import { AuthService } from '../../core/services/auth.service';
import { Appointment } from '../../core/models/appointment.model';

@Component({
  selector: 'app-appointments',
  standalone: true,
  imports: [CommonModule, NavbarComponent, RouterLink, FormsModule],
  templateUrl: './appointments.component.html',
  styleUrl: './appointments.component.css'
})
export class AppointmentsComponent implements OnInit {
  appointmentService = inject(AppointmentService);
  auth = inject(AuthService);

  appointments: Appointment[] = [];
  loading = true;
  cancellingId: string | null = null;
  updatingId: string | null = null;
  successMsg = '';
  errorMsg = '';

  // Completion modal state
  showCompleteModal = false;
  completingAptId: string | null = null;
  completionNotes = '';

  get user() { return this.auth.currentUser(); }
  get isDoctor() { return this.user?.role === 'DOCTOR'; }

  get pending() { return this.appointments.filter(a => a.status === 'PENDING'); }
  get accepted() { return this.appointments.filter(a => a.status === 'ACCEPTED'); }
  get past() { return this.appointments.filter(a => ['COMPLETED','REJECTED','CANCELLED'].includes(a.status)); }

  ngOnInit() { this.loadAppointments(); }

  loadAppointments() {
    this.loading = true;
    this.appointmentService.getAppointments().subscribe({
      next: (res) => {
        if (res.success && res.data) {
          this.appointments = (res.data as Appointment[]).sort((a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          );
        }
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  cancelAppointment(id: string) {
    if (!confirm('Are you sure you want to cancel this appointment?')) return;
    this.cancellingId = id;
    this.successMsg = '';
    this.errorMsg = '';
    this.appointmentService.cancelAppointment(id).subscribe({
      next: (res) => {
        if (res.success) {
          this.successMsg = 'Appointment cancelled successfully.';
          this.loadAppointments();
        } else {
          this.errorMsg = res.message || 'Failed to cancel.';
        }
        this.cancellingId = null;
      },
      error: (err: { error?: { message?: string } }) => {
        this.errorMsg = err.error?.message || 'Something went wrong.';
        this.cancellingId = null;
      }
    });
  }

  updateStatus(id: string, status: string, notes: string = '') {
    this.updatingId = id;
    this.errorMsg = '';
    
    this.appointmentService.updateAppointmentStatus(id, status, notes).subscribe({
      next: (res) => {
        if (res.success) {
          this.successMsg = `Appointment ${status.toLowerCase()} successfully.`;
          this.loadAppointments();
          setTimeout(() => this.successMsg = '', 3000);
        } else {
          this.errorMsg = res.message || 'Failed to update status.';
        }
        this.updatingId = null;
        this.closeCompleteModal();
      },
      error: () => { 
        this.errorMsg = 'Failed to update status.'; 
        this.updatingId = null;
        this.closeCompleteModal();
      }
    });
  }

  // ── Completion Modal ──────────────────────────────────────────────
  openCompleteModal(aptId: string) {
    this.completingAptId = aptId;
    this.completionNotes = '';
    this.showCompleteModal = true;
  }

  closeCompleteModal() {
    this.showCompleteModal = false;
    this.completingAptId = null;
    this.completionNotes = '';
  }

  submitCompletion() {
    if (this.completingAptId) {
      this.updateStatus(this.completingAptId, 'COMPLETED', this.completionNotes);
    }
  }

  statusClass(status: string): string {
    const map: Record<string, string> = {
      PENDING: 'status-pending',
      ACCEPTED: 'status-accepted',
      REJECTED: 'status-rejected',
      COMPLETED: 'status-completed',
      CANCELLED: 'status-cancelled',
    };
    return map[status] || '';
  }

  statusIcon(status: string): string {
    const map: Record<string, string> = {
      PENDING: '⏳', ACCEPTED: '✅', REJECTED: '❌', COMPLETED: '🏁', CANCELLED: '🚫'
    };
    return map[status] || '📋';
  }
}
