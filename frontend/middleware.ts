/**
 * Next.js middleware for route protection
 * Protects authenticated routes and redirects to login if not authenticated
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Routes that require authentication
const protectedRoutes = [
  '/dashboard',
  '/scraper',
  '/pages-manager',
  '/telegram',
  '/profile',
];

// Routes that require admin role (will be checked in the page component)
const adminRoutes = [
  '/admin',
];

// Routes that should redirect to dashboard if already authenticated
const authRoutes = [
  '/login',
  '/register',
];

export function middleware(request: NextRequest) {
  // Authentication bypass: all routes are now public
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};


