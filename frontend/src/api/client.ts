const API_BASE_URL = `${import.meta.env.VITE_API_URL}/api/v1`;

export const getStoredAccessToken = (): string | null => {
  return localStorage.getItem('shadowwatch_access_token');
};

export const getStoredRefreshToken = (): string | null => {
  return localStorage.getItem('shadowwatch_refresh_token');
};

export const setStoredTokens = (access: string, refresh: string) => {
  localStorage.setItem('shadowwatch_access_token', access);
  localStorage.setItem('shadowwatch_refresh_token', refresh);
};

export const clearStoredTokens = () => {
  localStorage.removeItem('shadowwatch_access_token');
  localStorage.removeItem('shadowwatch_refresh_token');
};

interface RequestOptions extends RequestInit {
  requiresAuth?: boolean;
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { requiresAuth = true, headers: customHeaders, ...restOptions } = options;
  const headers = new Headers(customHeaders);
  headers.set('Content-Type', 'application/json');

  if (requiresAuth) {
    const token = getStoredAccessToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers,
    ...restOptions,
  });

  // Handle unauthorized (401)
  if (response.status === 401 && requiresAuth) {
    // Attempt token refresh if refresh token exists
    const refreshToken = getStoredRefreshToken();
    if (refreshToken && !endpoint.includes('/auth/refresh')) {
      try {
        const refreshResponse = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (refreshResponse.ok) {
          const newTokens = await refreshResponse.json();
          setStoredTokens(newTokens.access_token, newTokens.refresh_token);
          // Retry original request with new token
          headers.set('Authorization', `Bearer ${newTokens.access_token}`);
          const retryResponse = await fetch(url, { headers, ...restOptions });
          if (retryResponse.ok) {
            return (await retryResponse.json()) as T;
          }
        }
      } catch {
        // Refresh failed, proceed to wipe tokens
      }
    }

    clearStoredTokens();
    window.dispatchEvent(new CustomEvent('auth:expired'));
    throw new Error('Session expired. Please log in again.');
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMessage =
      data.detail || data.message || `Request failed with status ${response.status}`;
    throw new Error(errorMessage);
  }

  return data as T;
}
