/**
 * Type for the structure of the data object in Axios errors
 */
export interface AxiosErrorData {
  error?: {
    message?: string;
    details?: { loc: string[]; msg: string; type: string }[];
  };
}

/**
 * Interface for individual validation errors returned by the API.
 */
export interface ValidationError {
  field: string; // Field where the error occurred (e.g., "body.internal_id")
  message: string; // Error message for the field
  type: string; // Type of validation error (e.g., "missing")
}

/**
 * Interface for structured API error responses.
 */
export interface ApiError {
  statusCode: number; // HTTP status code (e.g., 400, 422, etc.)
  message: string; // General error message returned by the API
  validationErrors?: ValidationError[]; // List of field-level validation errors (optional)
}
