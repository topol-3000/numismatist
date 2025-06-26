/**
 * Validation result structure.
 */
export interface ValidationResult {
  valid: boolean;
  message?: string;
}

/**
 * Validates if a string is not empty.
 * @param value - Input value.
 * @returns ValidationResult
 */
export const required = (value: string): ValidationResult => {
  const isValid = value.trim().length > 0;
  return {
    valid: isValid,
    message: isValid ? undefined : "This field is required.",
  };
};

/**
 * Validates if a string matches a specific length range.
 * @param value - Input value.
 * @param min - Minimum length.
 * @param max - Maximum length.
 * @returns ValidationResult
 */
export const lengthRange = (
  value: string,
  min: number,
  max: number,
): ValidationResult => {
  const isValid = value.length >= min && value.length <= max;
  return {
    valid: isValid,
    message: isValid
      ? undefined
      : `Length must be between ${min} and ${max} characters.`,
  };
};

/**
 * Validates if a string is a valid email.
 * @param value - Input value.
 * @returns ValidationResult
 */
export const email = (value: string): ValidationResult => {
  const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  return {
    valid: isValid,
    message: isValid ? undefined : "Enter a valid email address.",
  };
};

/**
 * Combines multiple validation rules.
 * @param value - Input value.
 * @param rules - Array of validation functions.
 * @returns ValidationResult
 */
export const validate = (
  value: string,
  rules: Array<(value: string) => ValidationResult>,
): ValidationResult => {
  for (const rule of rules) {
    const result = rule(value);
    if (!result.valid) {
      return result;
    }
  }
  return { valid: true };
};
