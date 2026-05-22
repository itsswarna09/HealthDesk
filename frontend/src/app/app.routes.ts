import { Routes } from '@angular/router';
import { authGuard, guestGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  // Redirect root to dashboard (guard handles redirect to login if not logged in)
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },

  // Public routes — logged-in users get redirected to dashboard
  {
    path: 'login',
    canActivate: [guestGuard],
    loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    canActivate: [guestGuard],
    loadComponent: () => import('./pages/register/register.component').then(m => m.RegisterComponent)
  },

  // Protected routes — requires JWT token
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent)
  },
  {
    path: 'profile',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/profile/profile.component').then(m => m.ProfileComponent)
  },
  {
    path: 'appointments',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/appointments/appointments.component').then(m => m.AppointmentsComponent)
  },
  {
    path: 'records',
    canActivate: [authGuard, roleGuard],
    data: { role: 'PATIENT' },
    loadComponent: () => import('./pages/records/records.component').then(m => m.RecordsComponent)
  },
  {
    path: 'doctors',
    canActivate: [authGuard, roleGuard],
    data: { role: 'PATIENT' },
    loadComponent: () => import('./pages/doctors/doctor-list/doctor-list.component').then(m => m.DoctorListComponent)
  },
  {
    path: 'doctors/:id',
    canActivate: [authGuard],
    loadComponent: () => import('./pages/doctors/doctor-detail/doctor-detail.component').then(m => m.DoctorDetailComponent)
  },

  // Fallback
  { path: '**', redirectTo: 'dashboard' }
];
