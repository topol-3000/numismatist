import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useLocalStorage } from '@vueuse/core'
import { authApi } from '@/services/api/auth'
import type { User, LoginCredentials, RegisterData } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State - using @vueuse/core for localStorage
  const user = ref<User | null>(null)
  const token = useLocalStorage<string | null>('authToken', null)
  const isLoading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_superuser || false)

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      isLoading.value = true

      const response = await authApi.login(credentials)
      token.value = response.access_token

      // Fetch user data after successful login
      const userData = await authApi.getCurrentUser()
      user.value = userData

      return true
    } catch (err) {
      console.error('Login failed:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const register = async (data: RegisterData): Promise<boolean> => {
    try {
      isLoading.value = true

      await authApi.register(data)

      // Auto-login after registration
      const loginSuccess = await login({
        username: data.email,
        password: data.password,
      })

      return loginSuccess
    } catch (err) {
      console.error('Registration failed:', err)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = async (): Promise<void> => {
    try {
      if (token.value) {
        await authApi.logout()
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      token.value = null
      user.value = null
    }
  }

  const initializeAuth = async (): Promise<void> => {
    if (!token.value) return

    try {
      isLoading.value = true
      const userData = await authApi.getCurrentUser()
      user.value = userData
    } catch (err) {
      console.error('Failed to initialize auth:', err)
      // Clear invalid token
      token.value = null
      user.value = null
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    user,
    token,
    isLoading,

    // Getters
    isAuthenticated,
    isAdmin,

    // Actions
    login,
    register,
    logout,
    initializeAuth,
  }
})
