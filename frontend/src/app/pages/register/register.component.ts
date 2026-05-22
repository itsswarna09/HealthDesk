import { Component, inject } from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { RouterLink, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../core/services/auth.service';
import { ToastService } from '../../shared/toast/toast.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  private fb     = inject(FormBuilder);
  private auth   = inject(AuthService);
  private toast  = inject(ToastService);
  private router = inject(Router);

  loading = false;

  bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'UNKNOWN'];
  roles       = [
    { value: 'PATIENT', label: 'Patient' },
    { value: 'DOCTOR',  label: 'Doctor' },
    { value: 'DONOR',   label: 'Blood Donor' },
  ];

  form = this.fb.group({
    first_name:  ['', [Validators.required, Validators.maxLength(100)]],
    last_name:   ['', [Validators.required, Validators.maxLength(100)]],
    email:       ['', [Validators.required, Validators.email]],
    phone:       [''],
    blood_group: ['UNKNOWN'],
    role:        ['PATIENT'],
    password:    ['', [Validators.required, Validators.minLength(8)]],
    password2:   ['', Validators.required],
  }, { validators: this.passwordMatch });

  passwordMatch(group: any) {
    const p1 = group.get('password')?.value;
    const p2 = group.get('password2')?.value;
    return p1 === p2 ? null : { mismatch: true };
  }

  submit() {
    if (this.form.invalid || this.loading) return;

    this.loading = true;
    this.auth.register(this.form.value).subscribe({
      next: (res) => {
        this.toast.success(res.message);
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        const msg = err.error?.message || 'Registration failed. Please try again.';
        this.toast.error(msg);
        this.loading = false;
      }
    });
  }

  get passwordMismatch() {
    return this.form.hasError('mismatch') && this.form.get('password2')?.touched;
  }
}
