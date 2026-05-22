import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DoctorService } from '../../../core/services/doctor.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastService } from '../../../shared/toast/toast.service';

@Component({
  selector: 'app-doctor-availability',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="card" *ngIf="isDoctor">
      <h2 class="card-title">🕒 Manage Availability & Schedule</h2>
      
      <div class="schedule-list">
        <div class="day-row" *ngFor="let day of days">
          <div class="day-toggle">
            <label class="switch">
              <input type="checkbox" [(ngModel)]="schedule[day].enabled" />
              <span class="slider round"></span>
            </label>
            <span class="day-name">{{ day | titlecase }}</span>
          </div>
          
          <div class="time-inputs" *ngIf="schedule[day].enabled">
            <input type="time" [(ngModel)]="schedule[day].start" class="form-input time-picker" />
            <span>to</span>
            <input type="time" [(ngModel)]="schedule[day].end" class="form-input time-picker" />
          </div>
          <div class="time-inputs text-muted" *ngIf="!schedule[day].enabled">
            Day Off
          </div>
        </div>
      </div>

      <div class="section-divider">Unavailable Dates (Vacation / Sick Leave)</div>
      <div class="unavailable-dates-section">
        <div class="add-date-row">
          <input type="date" [(ngModel)]="newUnavailableDate" [min]="minDate" class="form-input" style="max-width:200px;" />
          <button class="btn-outline" (click)="addUnavailableDate()">Add Date</button>
        </div>
        
        <div class="chips-container" style="margin-top: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem;">
          <span class="badge-specialty date-chip" *ngFor="let date of unavailableDates" style="display:flex; align-items:center; gap:5px;">
            {{ date | date:'mediumDate' }}
            <button class="chip-close" (click)="removeUnavailableDate(date)" style="background:transparent; border:none; color:inherit; cursor:pointer;">✕</button>
          </span>
          <span *ngIf="unavailableDates.length === 0" class="text-muted">No upcoming days off scheduled.</span>
        </div>
      </div>

      <button class="btn-primary" style="margin-top: 1.5rem; width: 100%;" (click)="saveAvailability()" [disabled]="loading">
        <span *ngIf="loading" class="spinner"></span> 
        <span *ngIf="!loading">Save Schedule</span>
      </button>
    </div>
  `,
  styles: [`
    .schedule-list { display: flex; flex-direction: column; gap: 1rem; margin-top: 1rem; }
    .day-row { display: flex; align-items: center; justify-content: space-between; padding: 10px; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }
    .day-toggle { display: flex; align-items: center; gap: 10px; width: 120px; }
    .day-name { font-weight: 500; }
    .time-inputs { display: flex; align-items: center; gap: 10px; flex: 1; justify-content: flex-end; }
    .time-picker { max-width: 130px; padding: 5px 10px; }
    .add-date-row { display: flex; gap: 10px; align-items: center; }
    .chip-close:hover { color: #ff4444 !important; }
    
    /* Toggle Switch */
    .switch { position: relative; display: inline-block; width: 34px; height: 20px; }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #333; transition: .4s; }
    .slider:before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background-color: white; transition: .4s; }
    input:checked + .slider { background-color: var(--primary); }
    input:checked + .slider:before { transform: translateX(14px); }
    .slider.round { border-radius: 34px; }
    .slider.round:before { border-radius: 50%; }
  `]
})
export class DoctorAvailabilityComponent implements OnInit {
  auth = inject(AuthService);
  doctorService = inject(DoctorService);
  toast = inject(ToastService);

  days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
  
  schedule: any = {
    monday: { enabled: true, start: '09:00', end: '17:00' },
    tuesday: { enabled: true, start: '09:00', end: '17:00' },
    wednesday: { enabled: true, start: '09:00', end: '17:00' },
    thursday: { enabled: true, start: '09:00', end: '17:00' },
    friday: { enabled: true, start: '09:00', end: '17:00' },
    saturday: { enabled: false, start: '09:00', end: '13:00' },
    sunday: { enabled: false, start: '', end: '' }
  };
  
  unavailableDates: string[] = [];
  newUnavailableDate: string = '';
  loading = false;

  get isDoctor() {
    return this.auth.currentUser()?.role === 'DOCTOR';
  }

  get minDate() {
    return new Date().toISOString().split('T')[0];
  }

  ngOnInit() {
    // If we had a GET endpoint for profile we would load it here.
    // Since we don't, we'll start with defaults and they overwrite.
    // In a real app we'd fetch the doctor profile. For MVP this works as a direct setter.
  }

  addUnavailableDate() {
    if (!this.newUnavailableDate) return;
    if (!this.unavailableDates.includes(this.newUnavailableDate)) {
      this.unavailableDates.push(this.newUnavailableDate);
      this.unavailableDates.sort();
    }
    this.newUnavailableDate = '';
  }

  removeUnavailableDate(date: string) {
    this.unavailableDates = this.unavailableDates.filter(d => d !== date);
  }

  saveAvailability() {
    this.loading = true;
    this.doctorService.updateAvailability({
      schedule: this.schedule,
      unavailable_dates: this.unavailableDates
    }).subscribe({
      next: (res) => {
        this.toast.success(res.message || 'Availability updated.');
        this.loading = false;
      },
      error: (err) => {
        this.toast.error(err.error?.message || 'Failed to update availability.');
        this.loading = false;
      }
    });
  }
}
