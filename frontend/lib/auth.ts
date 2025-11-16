/**
 * Authentication utilities
 * Handles login, registration, token management, and authentication state
 */

import { getCookie, setCookie, deleteCookie } from 'cookies-next';

const TOKEN_COOKIE_NAME = 'linkpulse_token';
const TOKEN_EXPIRY_DAYS = 7;

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name?: string;
}

export interface User {
  id: number;
  email: string;
  name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

/**
 * Get API base URL
 */
const getApiBaseUrl = (): string => {
  if (typeof window === 'undefined') {
    return 'http://localhost:8000';
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

/**
 * Login user and store token in cookie
 */
export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const response = await fetch(`${getApiBaseUrl()}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(error.detail || 'Login failed');
  }

  const data: AuthResponse = await response.json();
  
  // Store token in cookie
  setCookie(TOKEN_COOKIE_NAME, data.access_token, {
    maxAge: TOKEN_EXPIRY_DAYS * 24 * 60 * 60, // Convert days to seconds
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  });

  return data;
}

/**
 * Register new user and automatically login
 */
export async function register(userData: RegisterData): Promise<{ user: User; token: AuthResponse }> {
  // Register user
  const registerResponse = await fetch(`${getApiBaseUrl()}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!registerResponse.ok) {
    const error = await registerResponse.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(error.detail || 'Registration failed');
  }

  const user: User = await registerResponse.json();

  // Auto-login after registration
  const tokenResponse = await login({
    email: userData.email,
    password: userData.password,
  });

  return { user, token: tokenResponse };
}

/**
 * Logout user (remove token from cookie)
 */
export function logout(): void {
  deleteCookie(TOKEN_COOKIE_NAME);
}

/**
 * Get stored token from cookie
 */
export function getToken(): string | undefined {
  const token = getCookie(TOKEN_COOKIE_NAME);
  return typeof token === 'string' ? token : undefined;
}

/**
 * Check if user is authenticated (has valid token)
 */
export function isAuthenticated(): boolean {
  return !!getToken();
}

/**
 * Get current user from token (calls /auth/me)
 */
export async function getCurrentUser(): Promise<User | null> {
  const token = getToken();
  if (!token) {
    return null;
  }

  try {
    const response = await fetch(`${getApiBaseUrl()}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      // Token invalid, remove it
      logout();
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching current user:', error);
    return null;
  }
}


