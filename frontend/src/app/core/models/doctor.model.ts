import { User } from './user.model';

export interface Doctor {
  id: string;
  user_id: string;
  specialization: string;
  experience_years: number;
  qualifications: string[];
  schedule: any;
  unavailable_dates: string[];
  consultation_fee: number;
  is_verified: boolean;
  user?: User; // Joined field
}
