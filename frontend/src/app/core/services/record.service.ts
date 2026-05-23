import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ApiResponse } from '../models/user.model';
import { MedicalRecord } from '../models/record.model';

@Injectable({ providedIn: 'root' })
export class RecordService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/records/`;

  getRecords(category?: string, patientId?: string): Observable<ApiResponse<MedicalRecord[]>> {
    let params = new HttpParams();
    if (category) params = params.set('category', category);
    if (patientId) params = params.set('patient_id', patientId);
    return this.http.get<ApiResponse<MedicalRecord[]>>(this.apiUrl, { params });
  }

  getCategories(): Observable<ApiResponse<string[]>> {
    return this.http.get<ApiResponse<string[]>>(`${this.apiUrl}categories/`);
  }

  uploadRecord(formData: FormData): Observable<ApiResponse<MedicalRecord>> {
    return this.http.post<ApiResponse<MedicalRecord>>(this.apiUrl, formData);
  }

  deleteRecord(id: string): Observable<ApiResponse<null>> {
    return this.http.delete<ApiResponse<null>>(`${this.apiUrl}${id}/`);
  }

  getDownloadUrl(id: string): string {
    return `${this.apiUrl}${id}/download/`;
  }

  downloadRecord(id: string): Observable<Blob> {
    const url = `${this.apiUrl}${id}/download/`;
    return this.http.get(url, { responseType: 'blob' });
  }
}
