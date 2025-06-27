export interface ApiError {
  message: string
  status?: number
  code?: string
  details?: Record<string, any>
}

export interface ApiResponse<T = any> {
  data: T
  status: number
  message?: string
}

export interface ValidationError {
  field: string
  message: string
}

export interface ErrorDetail {
  loc: (string | number)[]
  msg: string
  type: string
}
