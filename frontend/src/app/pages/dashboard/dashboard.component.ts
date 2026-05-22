import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { NavbarComponent } from '../../shared/navbar/navbar.component';
import { AuthService } from '../../core/services/auth.service';
import { AppointmentService } from '../../core/services/appointment.service';
import { Appointment } from '../../core/models/appointment.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, NavbarComponent, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  auth = inject(AuthService);
  appointmentService = inject(AppointmentService);

  appointments: Appointment[] = [];
  loadingAppointments = true;

  get user() { return this.auth.currentUser(); }

  ngOnInit() {
    // Refresh user data from server on page load
    this.auth.getProfile().subscribe();
    this.loadAppointments();
  }

  loadAppointments() {
    this.appointmentService.getAppointments().subscribe({
      next: (res) => {
        if (res.success && res.data) {
          this.appointments = res.data;
        }
        this.loadingAppointments = false;
      },
      error: () => {
        this.loadingAppointments = false;
      }
    });
  }

  getRoleBadgeClass(): string {
    const roles: Record<string, string> = {
      PATIENT: 'badge-patient',
      DOCTOR:  'badge-doctor',
      ADMIN:   'badge-admin',
      DONOR:   'badge-donor',
    };
    return roles[this.user?.role || ''] || 'badge-patient';
  }
}
