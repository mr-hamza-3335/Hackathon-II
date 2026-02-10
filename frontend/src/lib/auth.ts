/**
 * Auth utilities for logout and auth state.
 * T048: Create auth utilities in frontend/src/lib/auth.ts
 */

import { api, ApiError } from './api';
import { User } from '@/types';

/**
 * Get current user info (check if authenticated).
 */
export async function getCurrentUser(): Promise<User | null> {
  try {
    const user = await api.get<User>('/api/v1/auth/me');
    return user;
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }
    throw error;
  }
}

/**
 * Log out the current user.
 * FR-007: Allow users to log out, invalidating their session
 * FR-031: Clear authentication cookies on logout
 */
export async function logout(): Promise<void> {
  await api.post('/api/v1/auth/logout');
}

/**
 * Check if user is authenticated.
 */
export async function isAuthenticated(): Promise<boolean> {
  const user = await getCurrentUser();
  return user !== null;
}
