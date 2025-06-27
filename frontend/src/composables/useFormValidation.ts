import { ref, computed, reactive } from 'vue'

export interface ValidationRule {
  required?: boolean
  email?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: string) => string | null
}

export interface ValidationMessage {
  text: string
  type: 'error' | 'warning' | 'success'
}

export interface FieldState {
  value: string
  error: string | null
  touched: boolean
  valid: boolean
  messages: ValidationMessage[]
}

export interface FormField {
  rules: ValidationRule
  state: FieldState
}

export function useFormValidation<T extends Record<string, ValidationRule>>(fields: T) {
  // Create reactive field states
  const fieldStates = reactive<Record<string, FieldState>>(
    Object.keys(fields).reduce((acc, key) => {
      acc[key] = {
        value: '',
        error: null,
        touched: false,
        valid: false,
        messages: []
      }
      return acc
    }, {} as Record<string, FieldState>)
  )

  const isFormValid = computed(() => {
    return Object.values(fieldStates).every(field => field.valid || !field.touched)
  })

  const hasErrors = computed(() => {
    return Object.values(fieldStates).some(field => 
      field.error || field.messages.some((m: ValidationMessage) => m.type === 'error')
    )
  })

  const touchedFields = computed(() => {
    return Object.values(fieldStates).filter(field => field.touched)
  })

  const validateField = (fieldName: keyof T, value: string): ValidationMessage[] => {
    const rules = fields[fieldName]
    const messages: ValidationMessage[] = []
    
    // Required validation
    if (rules.required && !value.trim()) {
      messages.push({
        text: `${String(fieldName).charAt(0).toUpperCase() + String(fieldName).slice(1)} is required`,
        type: 'error'
      })
      return messages
    }

    // Skip other validations if field is empty and not required
    if (!value.trim() && !rules.required) {
      return messages
    }

    // Email validation
    if (rules.email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(value)) {
        messages.push({
          text: 'Please enter a valid email address',
          type: 'error'
        })
      }
    }

    // Length validations
    if (rules.minLength && value.length < rules.minLength) {
      messages.push({
        text: `Must be at least ${rules.minLength} characters long`,
        type: 'error'
      })
    }

    if (rules.maxLength && value.length > rules.maxLength) {
      messages.push({
        text: `Must be no more than ${rules.maxLength} characters long`,
        type: 'error'
      })
    }

    // Pattern validation
    if (rules.pattern && !rules.pattern.test(value)) {
      messages.push({
        text: 'Invalid format',
        type: 'error'
      })
    }

    // Custom validation
    if (rules.custom) {
      const customError = rules.custom(value)
      if (customError) {
        messages.push({
          text: customError,
          type: 'error'
        })
      }
    }

    // Password strength recommendations (for password fields)
    if (String(fieldName).toLowerCase().includes('password') && value) {
      if (!/(?=.*[a-z])/.test(value)) {
        messages.push({
          text: 'Include lowercase letters for better security',
          type: 'warning'
        })
      }
      if (!/(?=.*[A-Z])/.test(value)) {
        messages.push({
          text: 'Include uppercase letters for better security',
          type: 'warning'
        })
      }
      if (!/(?=.*[0-9])/.test(value)) {
        messages.push({
          text: 'Include numbers for better security',
          type: 'warning'
        })
      }
      if (!/(?=.*[^A-Za-z0-9])/.test(value)) {
        messages.push({
          text: 'Include special characters for better security',
          type: 'warning'
        })
      }
    }

    return messages
  }

  const updateField = (fieldName: keyof T, value: string) => {
    const field = fieldStates[String(fieldName)]
    if (field) {
      field.value = value
      field.messages = validateField(fieldName, value)
      field.error = field.messages.find((m: ValidationMessage) => m.type === 'error')?.text || null
      field.valid = !field.messages.some((m: ValidationMessage) => m.type === 'error')
    }
  }

  const touchField = (fieldName: keyof T) => {
    const field = fieldStates[String(fieldName)]
    if (field) {
      field.touched = true
    }
  }

  const validateAllFields = (): boolean => {
    let isValid = true
    
    Object.keys(fields).forEach(key => {
      const fieldName = key as keyof T
      const field = fieldStates[String(fieldName)]
      if (field) {
        field.touched = true
        field.messages = validateField(fieldName, field.value)
        field.error = field.messages.find((m: ValidationMessage) => m.type === 'error')?.text || null
        field.valid = !field.messages.some((m: ValidationMessage) => m.type === 'error')
        
        if (!field.valid) {
          isValid = false
        }
      }
    })
    
    return isValid
  }

  const resetForm = () => {
    Object.keys(fieldStates).forEach(key => {
      const field = fieldStates[key]
      if (field) {
        field.value = ''
        field.error = null
        field.touched = false
        field.valid = false
        field.messages = []
      }
    })
  }

  const getFieldValue = (fieldName: keyof T): string => {
    return fieldStates[String(fieldName)]?.value || ''
  }

  const setFieldValue = (fieldName: keyof T, value: string) => {
    updateField(fieldName, value)
  }

  const getFieldError = (fieldName: keyof T): string | null => {
    return fieldStates[String(fieldName)]?.error || null
  }

  const getFieldMessages = (fieldName: keyof T): ValidationMessage[] => {
    return fieldStates[String(fieldName)]?.messages || []
  }

  const isFieldTouched = (fieldName: keyof T): boolean => {
    return fieldStates[String(fieldName)]?.touched || false
  }

  const isFieldValid = (fieldName: keyof T): boolean => {
    return fieldStates[String(fieldName)]?.valid || false
  }

  return {
    // State
    fieldStates,
    isFormValid,
    hasErrors,
    touchedFields,
    
    // Methods
    validateField,
    updateField,
    touchField,
    validateAllFields,
    resetForm,
    
    // Field helpers
    getFieldValue,
    setFieldValue,
    getFieldError,
    getFieldMessages,
    isFieldTouched,
    isFieldValid
  }
}

// Common validation rules
export const commonRules = {
  required: { required: true },
  email: { required: true, email: true },
  password: { required: true, minLength: 8 },
  strongPassword: {
    required: true,
    minLength: 8,
    custom: (value: string) => {
      const hasLower = /(?=.*[a-z])/.test(value)
      const hasUpper = /(?=.*[A-Z])/.test(value)
      const hasNumber = /(?=.*[0-9])/.test(value)
      const hasSpecial = /(?=.*[^A-Za-z0-9])/.test(value)
      
      if (!hasLower || !hasUpper || !hasNumber || !hasSpecial) {
        return 'Password must contain uppercase, lowercase, number, and special character'
      }
      return null
    }
  }
}
