/**
 * API client wrapper with credentials for cookie-based auth.
 * T024: Create API client wrapper with credentials:include in frontend/src/lib/api.ts
 *
 * SECURITY: Handles 401 errors globally with auto-redirect to login.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Auth error event for global handling
const AUTH_ERROR_EVENT = 'pakaura:auth-error';

export class ApiError extends Error {
  code: string;
  details: Array<{ field: string; message: string }>;
  status: number;

  constructor(
    message: string,
    code: string,
    status: number,
    details: Array<{ field: string; message: string }> = []
  ) {
    super(message);
    this.code = code;
    this.status = status;
    this.details = details;
    this.name = 'ApiError';
  }
}

interface ApiResponse<T> {
  data?: T;
  error?: {
    code: string;
    message: string;
    details: Array<{ field: string; message: string }>;
  };
}

/**
 * Dispatch auth error event for global handling.
 * Components can listen to this to clear state and redirect.
 */
function dispatchAuthError(): void {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent(AUTH_ERROR_EVENT));
  }
}

/**
 * Subscribe to auth error events.
 * Returns cleanup function to unsubscribe.
 */
export function onAuthError(callback: () => void): () => void {
  if (typeof window === 'undefined') return () => {};

  const handler = () => callback();
  window.addEventListener(AUTH_ERROR_EVENT, handler);
  return () => window.removeEventListener(AUTH_ERROR_EVENT, handler);
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    credentials: 'include', // Send cookies with every request
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  // Handle no content responses
  if (response.status === 204) {
    return {} as T;
  }

  const data = await response.json();

  if (!response.ok) {
    const error = data.error || data.detail?.error || { code: 'UNKNOWN_ERROR', message: 'An error occurred', details: [] };

    // Handle 401 errors globally - auto redirect to login
    // Skip redirect for auth endpoints (login/register) to show proper error messages
    if (response.status === 401 && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
      dispatchAuthError();
    }

    throw new ApiError(
      error.message,
      error.code,
      response.status,
      error.details || []
    );
  }

  return data as T;
}

// Convenience methods
export const api = {
  get: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'GET' }),

  post: <T>(endpoint: string, body?: unknown) =>
    apiRequest<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(endpoint: string, body: unknown) =>
    apiRequest<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),

  delete: <T>(endpoint: string) =>
    apiRequest<T>(endpoint, { method: 'DELETE' }),
};
