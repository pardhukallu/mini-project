import { apiClient, clearStoredTokens, setStoredTokens, getStoredRefreshToken } from './client';
import type { AuthResponse, DashboardOverview, User } from '../types/auth';

export async function registerApi(
  email: string,
  password: string,
  fullName?: string
): Promise<AuthResponse> {
  const data = await apiClient<AuthResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      email,
      password,
      full_name: fullName || '',
    }),
    requiresAuth: false,
  });

  if (data.tokens) {
    setStoredTokens(data.tokens.access_token, data.tokens.refresh_token);
  }
  return data;
}

export async function loginApi(
  email: string,
  password: string
): Promise<AuthResponse> {
  const data = await apiClient<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
    requiresAuth: false,
  });

  if (data.tokens) {
    setStoredTokens(data.tokens.access_token, data.tokens.refresh_token);
  }
  return data;
}

export async function getCurrentUserApi(): Promise<User> {
  return apiClient<User>('/auth/me', {
    method: 'GET',
    requiresAuth: true,
  });
}

export async function logoutApi(): Promise<void> {
  try {
    await apiClient('/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: getStoredRefreshToken() }),
      requiresAuth: true,
    });
  } catch {
    // Ignore backend logout errors, always clear locally
  } finally {
    clearStoredTokens();
  }
}

export async function getDashboardOverviewApi(): Promise<DashboardOverview> {
  return apiClient<DashboardOverview>('/dashboard/overview', {
    method: 'GET',
    requiresAuth: true,
  });
}
