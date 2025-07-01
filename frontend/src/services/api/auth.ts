import { httpClient } from '@/services/http'
import type { LoginCredentials, RegisterData, User, LoginResponse } from '@/types'

export const authApi = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await httpClient.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  },

  async register(data: RegisterData): Promise<User> {
    const response = await httpClient.post<User>('/auth/register', data)
    return response.data
  },

  async logout(): Promise<void> {
    await httpClient.post('/auth/logout')
  },

  async getCurrentUser(): Promise<User> {
    const response = await httpClient.get<User>('/users/me')
    return response.data
  },
}
