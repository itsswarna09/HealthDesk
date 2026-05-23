import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/user.model';

export interface BloodDonor {
  id: string;
  user_id: string;
  blood_group: string;
  city: string;
  phone: string;
  last_donated_date?: string;
  is_available: boolean;
  user?: {
    first_name: string;
    last_name: string;
    email: string;
  };
}

export interface BloodRequest {
  id: string;
  patient_id: string;
  blood_group: string;
  units_required: number;
  urgency: string;
  hospital_name: string;
  address_line?: string;
  city: string;
  state?: string;
  zip_code?: string;
  contact_name: string;
  contact_phone: string;
  reason?: string;
  status: string;
  rejection_reason?: string;
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class BloodService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/blood-requests/`;

  // -- Donors --
  getMyDonorProfile(): Observable<ApiResponse<BloodDonor>> {
    return this.http.get<ApiResponse<BloodDonor>>(`${this.apiUrl}donors/me/`);
  }

  registerAsDonor(data: any): Observable<ApiResponse<BloodDonor>> {
    return this.http.post<ApiResponse<BloodDonor>>(`${this.apiUrl}donors/me/`, data);
  }

  getDonors(bloodGroup?: string, city?: string): Observable<ApiResponse<BloodDonor[]>> {
    let params = new HttpParams();
    if (bloodGroup) params = params.set('blood_group', bloodGroup);
    if (city) params = params.set('city', city);
    return this.http.get<ApiResponse<BloodDonor[]>>(`${this.apiUrl}donors/`, { params });
  }

  // -- Requests --
  getRequests(bloodGroup?: string, city?: string, status?: string): Observable<ApiResponse<BloodRequest[]>> {
    let params = new HttpParams();
    if (bloodGroup) params = params.set('blood_group', bloodGroup);
    if (city) params = params.set('city', city);
    if (status) params = params.set('status', status);
    return this.http.get<ApiResponse<BloodRequest[]>>(`${this.apiUrl}requests/`, { params });
  }

  createRequest(data: any): Observable<ApiResponse<BloodRequest>> {
    return this.http.post<ApiResponse<BloodRequest>>(`${this.apiUrl}requests/`, data);
  }

  updateRequest(id: string, data: any): Observable<ApiResponse<null>> {
    return this.http.patch<ApiResponse<null>>(`${this.apiUrl}requests/${id}/`, data);
  }

  getOptions(): Observable<ApiResponse<any>> {
    return this.http.get<ApiResponse<any>>(`${this.apiUrl}options/`);
  }
}
