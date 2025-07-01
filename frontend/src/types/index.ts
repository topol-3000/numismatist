// Auth related types
export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
}

export interface User {
  id: string
  email: string
  is_active: boolean
  is_superuser: boolean
  is_verified: boolean
  created_at?: string
  updated_at?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}
