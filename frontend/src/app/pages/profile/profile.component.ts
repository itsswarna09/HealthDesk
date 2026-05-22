import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../../shared/navbar/navbar.component';
import { AuthService } from '../../core/services/auth.service';
import { ToastService } from '../../shared/toast/toast.service';

import { DoctorAvailabilityComponent } from './doctor-availability/doctor-availability.component';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule, NavbarComponent, DoctorAvailabilityComponent],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css'
})
export class ProfileComponent implements OnInit {
  private fb    = inject(FormBuilder);
  private auth  = inject(AuthService);
  private toast = inject(ToastService);

  loadingProfile = false;
  loadingPassword = false;

  bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'UNKNOWN'];

  profileForm = this.fb.group({
    first_name:               ['', Validators.required],
    last_name:                ['', Validators.required],
    phone:                    [''],
    blood_group:              ['UNKNOWN'],
    gender:                   [''],
    blood_donor_available:    [false],
    address_street:           [''],
    address_city:             [''],
    address_state:            [''],
    address_zip:              [''],
    emergency_contact_name:   [''],
    emergency_contact_phone:  [''],
  });

  passwordForm = this.fb.group({
    old_password:  ['', Validators.required],
    new_password:  ['', [Validators.required, Validators.minLength(8)]],
    new_password2: ['', Validators.required],
  }, { validators: (g) => {
    const p = g.get('new_password')?.value;
    const p2 = g.get('new_password2')?.value;
    return p === p2 ? null : { mismatch: true };
  }});

  ngOnInit() {
    const user = this.auth.currentUser();
    if (user) {
      this.profileForm.patchValue({
        first_name:              user.first_name,
        last_name:               user.last_name,
        phone:                   user.phone ?? '',
        blood_group:             user.blood_group,
        gender:                  user.gender ?? '',
        blood_donor_available:   user.blood_donor_available ?? false,
        address_street:          user.address?.street ?? '',
        address_city:            user.address?.city ?? '',
        address_state:           user.address?.state ?? '',
        address_zip:             user.address?.zip ?? '',
        emergency_contact_name:  user.emergency_contact?.name ?? '',
        emergency_contact_phone: user.emergency_contact?.phone ?? '',
      });
    }
  }

  saveProfile() {
    if (this.profileForm.invalid || this.loadingProfile) return;
    this.loadingProfile = true;

    this.auth.updateProfile(this.profileForm.value).subscribe({
      next: (res) => {
        this.toast.success(res.message);
        this.loadingProfile = false;
      },
      error: (err) => {
        this.toast.error(err.error?.message || 'Update failed.');
        this.loadingProfile = false;
      }
    });
  }

  changePassword() {
    if (this.passwordForm.invalid || this.loadingPassword) return;
    this.loadingPassword = true;

    this.auth.changePassword(this.passwordForm.value).subscribe({
      next: (res) => {
        this.toast.success(res.message);
        this.passwordForm.reset();
        this.loadingPassword = false;
      },
      error: (err) => {
        this.toast.error(err.error?.message || 'Password change failed.');
        this.loadingPassword = false;
      }
    });
  }

  get user() { return this.auth.currentUser(); }
  get passwordMismatch() {
    return this.passwordForm.hasError('mismatch') && this.passwordForm.get('new_password2')?.touched;
  }
}
