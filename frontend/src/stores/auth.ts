import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useStorage } from '@vueuse/core'
import { authService } from '@/services/auth'
import type { User, RegisterData } from '@/types/auth'
import type { ApiError } from '@/types/api'
import apiClient from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = useStorage<string | null>('auth_token', null, localStorage, {
    mergeDefaults: true,
  })
  
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<ApiError | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Watch token changes and update API client
  watch(
    token,
    (newToken) => {
      apiClient.setAuthToken(newToken)
    },
    { immediate: true }
  )

  // Set up unauthorized callback
  const handleUnauthorized = () => {
    logout()
  }
  
  apiClient.setUnauthorizedCallback(handleUnauthorized)

  // Actions
  const setToken = (newToken: string | null) => {
    token.value = newToken
    // The watch function above will handle API client update and event emission
  }

  const setUser = (newUser: User | null) => {
    user.value = newUser
  }

  const setError = (newError: ApiError | null) => {
    error.value = newError
  }

  const clearError = () => {
    error.value = null
  }

  const login = async (email: string, password: string, rememberMe: boolean = false): Promise<boolean> => {
    isLoading.value = true
    clearError()

    try {
      const response = await authService.login({ email, password })
      
      setToken(response.access_token)
      
      // Get user information
      await fetchUserInfo()
      
      // If not remembering, we could set a shorter expiration
      // For now, we rely on the backend token expiration
      
      return true
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData: RegisterData): Promise<boolean> => {
    isLoading.value = true
    clearError()

    try {
      const newUser = await authService.register(userData)
      setUser(newUser)
      return true
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = async (): Promise<void> => {
    isLoading.value = true
    
    try {
      await authService.logout()
    } catch (err) {
      console.warn('Logout API call failed:', err)
    } finally {
      // Clear local state regardless of API response
      setToken(null)
      setUser(null)
      clearError()
      isLoading.value = false
    }
  }

  const fetchUserInfo = async (): Promise<boolean> => {
    if (!token.value) {
      return false
    }

    try {
      const userData = await authService.getCurrentUser()
      setUser(userData)
      return true
    } catch (err) {
      const apiError = err as ApiError
      
      // If unauthorized, clear auth state
      if (apiError.status === 401) {
        setToken(null)
        setUser(null)
      }
      
      setError(apiError)
      return false
    }
  }

  const requestPasswordReset = async (email: string): Promise<boolean> => {
    isLoading.value = true
    clearError()

    try {
      await authService.requestPasswordReset({ email })
      return true
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // Initialize auth on store creation
  const initialize = async (): Promise<void> => {
    if (token.value) {
      setToken(token.value) // This sets up the API client
      await fetchUserInfo()
    }
  }

  return {
    // State
    token: computed(() => token.value),
    error: computed(() => error.value),
    isLoading: computed(() => isLoading.value),
    
    // Getters
    isAuthenticated,
    
    // Actions
    login,
    register,
    logout,
    requestPasswordReset,
    initialize,
    setError, // Expose setError for manual error handling
  }
})
