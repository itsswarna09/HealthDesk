import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <nav class="navbar">
      <div class="nav-brand">
        <span class="brand-icon">⚕</span>
        <span class="brand-name">HealthDesk</span>
      </div>
      <div class="nav-links">
        <a routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
        @if (auth.currentUser()?.role === 'PATIENT') {
          <a routerLink="/doctors" routerLinkActive="active">Find Doctors</a>
          <a routerLink="/records" routerLinkActive="active">Records</a>
        }
        <a routerLink="/appointments" routerLinkActive="active">
          {{ auth.currentUser()?.role === 'DOCTOR' ? 'Requests' : 'Appointments' }}
        </a>
        <a routerLink="/blood-donation" routerLinkActive="active">Blood Bank</a>
        <a routerLink="/profile" routerLinkActive="active">Profile</a>
        <button class="btn-logout" (click)="auth.logout()">Logout</button>
      </div>
    </nav>
  `,
  styles: [`
    .navbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 1rem 2.5rem;
      background: rgba(9, 9, 11, 0.85);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: var(--shadow-sm);
    }
    .nav-brand {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      font-size: 1.25rem;
      font-weight: 800;
      color: var(--text-main);
      letter-spacing: -0.02em;
    }
    .brand-icon { font-size: 1.6rem; color: var(--primary); }
    .nav-links {
      display: flex;
      align-items: center;
      gap: 1.5rem;
    }
    .nav-links a {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.95rem;
      font-weight: 600;
      transition: color 0.2s;
    }
    .nav-links a:hover,
    .nav-links a.active { color: var(--primary); }
    .btn-logout {
      background: rgba(244, 63, 94, 0.15);
      color: var(--danger);
      border: 1px solid rgba(244, 63, 94, 0.2);
      padding: 0.5rem 1.2rem;
      border-radius: var(--radius-sm);
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      backdrop-filter: blur(4px);
    }
    .btn-logout:hover { 
      background: rgba(244, 63, 94, 0.25);
      transform: translateY(-1px);
    }

    /* Mobile Responsiveness */
    @media (max-width: 640px) {
      .navbar {
        padding: 0.75rem 1rem;
      }
      .nav-brand {
        font-size: 1.1rem;
      }
      .brand-icon { font-size: 1.3rem; }
      .nav-links {
        gap: 0.75rem;
      }
      .nav-links a {
        font-size: 0.85rem;
      }
      .btn-logout {
        padding: 0.3rem 0.75rem;
        font-size: 0.8rem;
      }
    }
    @media (max-width: 400px) {
      .nav-brand .brand-name {
        display: none; /* Hide brand name on very small screens, show only icon */
      }
    }
  `]
})
export class NavbarComponent {
  auth = inject(AuthService);
}
