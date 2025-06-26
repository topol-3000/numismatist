import { AxiosError } from "axios";

import type { ApiError, AxiosErrorData, ValidationError } from "@/types/api.ts";

/**
 * Parses the raw Axios error into a structured ApiError object.
 * @param error - The error object received from an Axios request.
 * @returns A structured ApiError object.
 */
export function parseApiError(error: AxiosError<AxiosErrorData>): ApiError {
  // Handle errors with structured response (e.g., `error.response.data.error`)
  if (error.response?.data?.error) {
    const errorData = error.response.data.error;
    const validationErrors: ValidationError[] | undefined =
      errorData.details?.map(
        (detail: { loc: string[]; msg: string; type: string }) => ({
          field: detail.loc.slice(1).join("__"), // Convert field location array into a dot-separated string
          message: detail.msg, // Field-specific error message
          type: detail.type, // Validation error type
        }),
      );

    return {
      statusCode: error.response.status,
      message: errorData.message || "An unexpected error occurred",
      validationErrors,
    };
  }

  // Handle more general Axios errors (e.g., network issues)
  return {
    statusCode: error.response?.status || 500,
    message: error.message || "A network error occurred",
  };
}
