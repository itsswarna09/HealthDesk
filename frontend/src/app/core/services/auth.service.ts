import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { User, AuthResponse, ApiResponse } from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly api = environment.apiUrl;

  // Reactive signal — any component can read currentUser()
  currentUser = signal<User | null>(this.loadUserFromStorage());

  constructor(private http: HttpClient, private router: Router) {}

  // ── Auth Calls ────────────────────────────────────────────────

  register(data: object) {
    return this.http.post<AuthResponse>(`${this.api}/auth/register/`, data).pipe(
      tap(res => { if (res.success && res.data) this.saveSession(res.data.user, res.data.tokens); })
    );
  }

  login(email: string, password: string) {
    return this.http.post<AuthResponse>(`${this.api}/auth/login/`, { email, password }).pipe(
      tap(res => { if (res.success && res.data) this.saveSession(res.data.user, res.data.tokens); })
    );
  }

  logout() {
    const refresh = this.getRefreshToken();
    if (refresh) {
      // Fire-and-forget — blacklist server-side, clear client regardless
      this.http.post(`${this.api}/auth/logout/`, { refresh }).subscribe();
    }
    this.clearSession();
    this.router.navigate(['/login']);
  }

  getProfile() {
    return this.http.get<ApiResponse<{ user: User }>>(`${this.api}/auth/profile/`).pipe(
      tap(res => { if (res.success && res.data) this.currentUser.set(res.data.user); })
    );
  }

  updateProfile(data: object) {
    return this.http.put<ApiResponse<{ user: User }>>(`${this.api}/auth/profile/update/`, data).pipe(
      tap(res => { if (res.success && res.data) {
        this.currentUser.set(res.data.user);
        localStorage.setItem('hd_user', JSON.stringify(res.data.user));
      }})
    );
  }

  changePassword(data: object) {
    return this.http.put<ApiResponse>(`${this.api}/auth/change-password/`, data);
  }

  // ── Token Management ──────────────────────────────────────────

  getAccessToken(): string | null {
    return localStorage.getItem('hd_access');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('hd_refresh');
  }

  isLoggedIn(): boolean {
    return !!this.getAccessToken();
  }

  // ── Session Helpers ───────────────────────────────────────────

  private saveSession(user: User, tokens: { access: string; refresh: string }) {
    localStorage.setItem('hd_access', tokens.access);
    localStorage.setItem('hd_refresh', tokens.refresh);
    localStorage.setItem('hd_user', JSON.stringify(user));
    this.currentUser.set(user);
  }

  private clearSession() {
    localStorage.removeItem('hd_access');
    localStorage.removeItem('hd_refresh');
    localStorage.removeItem('hd_user');
    this.currentUser.set(null);
  }

  private loadUserFromStorage(): User | null {
    const raw = localStorage.getItem('hd_user');
    return raw ? JSON.parse(raw) : null;
  }
}
