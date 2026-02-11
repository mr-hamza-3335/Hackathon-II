/**
 * Next.js middleware for auth protection.
 * T049: Create Next.js middleware to redirect unauthenticated users to /login (FR-024)
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Paths that require authentication
const protectedPaths = ['/dashboard', '/assistant'];

// Paths that should redirect to dashboard if authenticated
const authPaths = ['/login', '/register'];

export function middleware(request: NextRequest) {
  // In cross-domain deployments (Vercel frontend + Render backend),
  // the auth_token cookie is set on the backend domain and is NOT visible
  // to Next.js server-side middleware. Checking it here causes a redirect
  // loop because the cookie is never found.
  //
  // Auth protection is handled client-side in the protected layout
  // via API call to /api/v1/auth/me with credentials: 'include'.
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - api routes
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
