export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string | null;
  date_of_birth: string | null;
  gender: string | null;
  profile_photo_url: string | null;
  role: 'PATIENT' | 'DOCTOR' | 'ADMIN' | 'DONOR';
  blood_group: string;
  blood_donor_available: boolean;
  is_active: boolean;
  is_verified: boolean;
  emergency_contact: { name: string | null; phone: string | null };
  address: { street: string | null; city: string | null; state: string | null; zip: string | null };
  created_at: string | null;
  last_login: string | null;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  data?: {
    user: User;
    tokens: AuthTokens;
  };
  errors?: Record<string, string[]>;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data?: T;
  errors?: Record<string, string[]>;
}
