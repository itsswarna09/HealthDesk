import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/user.model';
import { Doctor } from '../models/doctor.model';

@Injectable({
  providedIn: 'root'
})
export class DoctorService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/appointments/doctors/`;

  getDoctors(specialization?: string): Observable<ApiResponse<Doctor[]>> {
    let params = new HttpParams();
    if (specialization) {
      params = params.set('specialization', specialization);
    }
    return this.http.get<ApiResponse<Doctor[]>>(this.apiUrl, { params });
  }

  getSpecializations(): Observable<ApiResponse<string[]>> {
    return this.http.get<ApiResponse<string[]>>(`${this.apiUrl}specializations/`);
  }

  getDoctorDetails(id: string): Observable<ApiResponse<Doctor>> {
    return this.http.get<ApiResponse<Doctor>>(`${this.apiUrl}${id}/`);
  }

  updateDoctorProfile(data: any): Observable<ApiResponse<Doctor>> {
    return this.http.put<ApiResponse<Doctor>>(`${this.apiUrl}profile/`, data);
  }

  updateAvailability(data: { schedule: any; unavailable_dates: string[] }): Observable<ApiResponse<Doctor>> {
    return this.http.put<ApiResponse<Doctor>>(`${this.apiUrl}availability/`, data);
  }
}
