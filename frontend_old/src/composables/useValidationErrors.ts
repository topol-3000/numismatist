import { ref } from "vue";
import type { Ref } from "vue";

import type { ValidationError } from "@/types/api.ts";

export function useValidationErrors() {
  // Reactive object to store validation errors in a key-value format
  const validationErrors: Ref<Record<string, string>> = ref({});

  /**
   * Populates validationErrors with error messages for specific fields,
   * allowing you to display errors near corresponding form inputs.
   *
   * @param {ValidationError[]} errors - Array of validation errors from the API.
   */
  const parseValidationErrors = (errors?: ValidationError[]): void => {
    if (!errors) {
      validationErrors.value = {}; // Clear errors if none are provided
      return;
    }

    // Map array of errors into a key-value format { fieldName: errorMessage }
    validationErrors.value = errors.reduce(
      (acc, error) => {
        acc[error.field] = error.message;
        return acc;
      },
      {} as Record<string, string>,
    );
  };

  return {
    validationErrors, // Expose reactive validation errors
    parseValidationErrors, // Expose the parser function for API responses
  };
}
