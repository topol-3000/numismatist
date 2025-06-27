export interface LoginCredentials {
  username: string // FastAPI-Users uses 'username' field for email
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterData {
  email: string
  password: string
  is_active?: boolean
  is_superuser?: boolean
  is_verified?: boolean
}

export interface User {
  id: number
  email: string
  is_active: boolean
  is_superuser: boolean
  is_verified: boolean
}

export interface AuthError {
  detail?: string
  message?: string
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirm {
  token: string
  password: string
}
