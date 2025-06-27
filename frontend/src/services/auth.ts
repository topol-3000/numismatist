import type { 
  LoginCredentials, 
  LoginResponse, 
  RegisterData, 
  User, 
  PasswordResetRequest 
} from '@/types/auth'
import apiClient from './api'

export class AuthService {
  /**
   * Login user with email and password
   * FastAPI-Users expects form data with 'username' field
   */
  async login(credentials: { email: string; password: string }): Promise<LoginResponse> {
    const loginData: LoginCredentials = {
      username: credentials.email, // FastAPI-Users uses 'username' for email
      password: credentials.password
    }

    return await apiClient.postForm<LoginResponse>('/auth/login', loginData)
  }

  /**
   * Register new user
   */
  async register(userData: RegisterData): Promise<User> {
    return await apiClient.post<User>('/auth/register', userData)
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout')
    } catch (error) {
      // Logout might fail if token is invalid, but we still want to clear local state
      console.warn('Logout request failed:', error)
    }
  }

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    return await apiClient.get<User>('/users/me')
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(data: PasswordResetRequest): Promise<void> {
    await apiClient.post('/auth/forgot-password', data)
  }

  /**
   * Reset password with token
   */
  async resetPassword(token: string, password: string): Promise<void> {
    await apiClient.post('/auth/reset-password', {
      token,
      password
    })
  }
}

// Export singleton instance
export const authService = new AuthService()
