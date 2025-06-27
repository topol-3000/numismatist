import type { ApiError, ErrorDetail } from '@/types/api'
import type { AxiosError } from 'axios'

export const parseApiError = (error: AxiosError): ApiError => {
  const response = error.response

  if (!response) {
    return {
      message: 'Network error - please check your connection',
      status: 0,
      code: 'NETWORK_ERROR'
    }
  }

  const status = response.status
  const responseData = response.data as any

  // Handle FastAPI validation errors
  if (status === 422 && responseData?.detail && Array.isArray(responseData.detail)) {
    const validationErrors = responseData.detail as ErrorDetail[]
    const fieldErrors = validationErrors
      .map((err: ErrorDetail) => `${err.loc.join('.')}: ${err.msg}`)
      .join(', ')
    
    return {
      message: `Validation error: ${fieldErrors}`,
      status,
      code: 'VALIDATION_ERROR',
      details: responseData.detail
    }
  }

  // Handle FastAPI-Users authentication errors
  if (status === 400 && responseData?.detail) {
    return {
      message: responseData.detail,
      status,
      code: 'AUTH_ERROR'
    }
  }

  // Handle other HTTP errors
  let message = 'An unexpected error occurred'
  
  if (typeof responseData?.detail === 'string') {
    message = responseData.detail
  } else if (typeof responseData?.message === 'string') {
    message = responseData.message
  } else if (status === 401) {
    message = 'Authentication required'
  } else if (status === 403) {
    message = 'Access forbidden'
  } else if (status === 404) {
    message = 'Resource not found'
  } else if (status === 500) {
    message = 'Internal server error'
  }

  return {
    message,
    status,
    code: `HTTP_${status}`,
    details: responseData
  }
}

export const formatValidationErrors = (details: ErrorDetail[]): Record<string, string> => {
  const errors: Record<string, string> = {}
  
  details.forEach((error) => {
    const field = error.loc.length > 1 ? error.loc[error.loc.length - 1] : error.loc[0]
    errors[String(field)] = error.msg
  })
  
  return errors
}
