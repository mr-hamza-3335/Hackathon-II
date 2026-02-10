/**
 * Client-side validation utilities.
 * T025: Create client-side validation utilities in frontend/src/lib/validation.ts
 */

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

/**
 * Validate email format.
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate password (FR-002: minimum 8 characters).
 */
export function isValidPassword(password: string): boolean {
  return password.length >= 8;
}

/**
 * Validate task title (FR-016: 1-500 characters, non-empty).
 */
export function isValidTaskTitle(title: string): boolean {
  const trimmed = title.trim();
  return trimmed.length >= 1 && trimmed.length <= 500;
}

/**
 * Validate registration form.
 */
export function validateRegistration(
  email: string,
  password: string
): ValidationResult {
  const errors: Record<string, string> = {};

  if (!email) {
    errors.email = 'Email is required';
  } else if (!isValidEmail(email)) {
    errors.email = 'Please enter a valid email address';
  }

  if (!password) {
    errors.password = 'Password is required';
  } else if (!isValidPassword(password)) {
    errors.password = 'Password must be at least 8 characters';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate login form.
 */
export function validateLogin(
  email: string,
  password: string
): ValidationResult {
  const errors: Record<string, string> = {};

  if (!email) {
    errors.email = 'Email is required';
  } else if (!isValidEmail(email)) {
    errors.email = 'Please enter a valid email address';
  }

  if (!password) {
    errors.password = 'Password is required';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate task form.
 */
export function validateTask(title: string): ValidationResult {
  const errors: Record<string, string> = {};

  if (!title || !title.trim()) {
    errors.title = 'Task title is required';
  } else if (title.length > 500) {
    errors.title = 'Task title must be 500 characters or less';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}
