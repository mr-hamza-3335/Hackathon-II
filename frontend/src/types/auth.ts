/**
 * TypeScript types for User.
 * T022: Create TypeScript types for User in frontend/src/types/auth.ts per data-model.md
 */

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthError {
  error: {
    code: string;
    message: string;
    details: Array<{
      field: string;
      message: string;
    }>;
  };
}
