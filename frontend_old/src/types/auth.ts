export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface SignUpData {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}
