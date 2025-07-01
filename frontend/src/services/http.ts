import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import { env } from '@/config/env'
import { useAuthStore } from '@/stores/auth'

// Base API configuration
const API_BASE_URL = env.API_URL

class HttpClient {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.api.interceptors.request.use((config) => {
      const authStore = useAuthStore()

      if (authStore.token) {
        config.headers.Authorization = `Bearer ${authStore.token}`
      }
      return config
    })

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Clear token on unauthorized
          const authStore = useAuthStore()
          authStore.token = null
          authStore.user = null
        }
        const message = error.response?.data?.detail || error.message || 'Request failed'
        throw new Error(message)
      },
    )
  }

  get<T>(url: string, config = {}) {
    return this.api.get<T>(url, config)
  }

  post<T>(url: string, data?: unknown, config = {}) {
    return this.api.post<T>(url, data, config)
  }

  put<T>(url: string, data?: unknown, config = {}) {
    return this.api.put<T>(url, data, config)
  }

  delete<T>(url: string, config = {}) {
    return this.api.delete<T>(url, config)
  }

  patch<T>(url: string, data?: unknown, config = {}) {
    return this.api.patch<T>(url, data, config)
  }
}

export const httpClient = new HttpClient()
