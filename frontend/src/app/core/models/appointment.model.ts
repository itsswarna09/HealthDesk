import { User } from './user.model';
import { Doctor } from './doctor.model';

export interface Appointment {
  id: string;
  patient_id: string;
  doctor_id: string;
  date: string;
  time_slot: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'COMPLETED' | 'CANCELLED';
  reason_for_visit: string;
  notes: string;
  created_at: string;
  patient?: User; // Joined field
  doctor?: Doctor; // Joined field
}
