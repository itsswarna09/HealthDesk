import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastService } from './toast.service';

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (toast.toast()) {
      <div class="toast" [class]="toast.toast()!.type">
        <span class="toast-icon">
          {{ toast.toast()!.type === 'success' ? '✓' : toast.toast()!.type === 'error' ? '✕' : 'ℹ' }}
        </span>
        {{ toast.toast()!.message }}
      </div>
    }
  `,
  styles: [`
    .toast {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 1rem 1.5rem;
      border-radius: 12px;
      font-size: 0.9rem;
      font-weight: 500;
      z-index: 9999;
      animation: slideIn 0.3s ease;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .toast.success { background: #10b981; color: #fff; }
    .toast.error   { background: #ef4444; color: #fff; }
    .toast.info    { background: #3b82f6; color: #fff; }
    .toast-icon { font-size: 1.1rem; font-weight: 700; }
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to   { transform: translateX(0);   opacity: 1; }
    }
  `]
})
export class ToastComponent {
  toast = inject(ToastService);
}
