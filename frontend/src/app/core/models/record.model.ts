export interface MedicalRecord {
  id: string;
  patient_id: string;
  title: string;
  category: string;
  description: string;
  doctor_name: string;
  record_date: string;
  file_name: string;
  file_size: number;
  file_type: string;
  created_at: string;
}
