import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import type { ApiError } from '@/types/api'
import { parseApiError } from '@/utils/ApiError'

class ApiClient {
  private instance: AxiosInstance
  private authToken: string | null = null
  private onUnauthorized: (() => void) | null = null

  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  // Set callback for unauthorized responses (called from auth store)
  setUnauthorizedCallback(callback: () => void) {
    this.onUnauthorized = callback
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.instance.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`
        }
        return config
      },
      (error) => Promise.reject(parseApiError(error))
    )

    // Response interceptor - handle 401 errors
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        const parsedError: ApiError = parseApiError(error)

        // Handle 401 errors globally
        if (parsedError.status === 401) {
          this.clearAuthToken()
          this.onUnauthorized?.()
        }

        console.error('API Error:', parsedError)
        return Promise.reject(parsedError)
      }
    )
  }

  setAuthToken(token: string | null) {
    this.authToken = token
  }

  private clearAuthToken() {
    this.authToken = null
  }

  // HTTP methods - only what we actually use
  async get<T>(url: string): Promise<T> {
    const response = await this.instance.get<T>(url)
    return response.data
  }

  async post<T>(url: string, data = {}): Promise<T> {
    const response = await this.instance.post<T>(url, data)
    return response.data
  }

  // Form data method for login (FastAPI-Users requirement)
  async postForm<T>(url: string, data: Record<string, any>): Promise<T> {
    const formData = new URLSearchParams()
    Object.entries(data).forEach(([key, value]) => {
      formData.append(key, String(value))
    })

    const response = await this.instance.post<T>(url, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  }
}

// Create singleton instance
const apiClient = new ApiClient()

export default apiClient
