const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const getAccessToken = () => localStorage.getItem('pillsync_access_token');
export const getRefreshToken = () => localStorage.getItem('pillsync_refresh_token');

export const setTokens = (access, refresh) => {
  localStorage.setItem('pillsync_access_token', access);
  if (refresh) localStorage.setItem('pillsync_refresh_token', refresh);
};

export const clearTokens = () => {
  localStorage.removeItem('pillsync_access_token');
  localStorage.removeItem('pillsync_refresh_token');
  localStorage.removeItem('pillsync_user');
};

async function refreshAccessToken() {
  const refresh = getRefreshToken();
  if (!refresh) return false;
  const response = await fetch(`${API_BASE}/accounts/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  });
  if (!response.ok) return false;
  const data = await response.json();
  setTokens(data.access, data.refresh);
  return true;
}

export async function apiFetch(path, options = {}, retry = true) {
  const headers = new Headers(options.headers || {});
  const token = getAccessToken();
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) headers.set('Authorization', `Bearer ${token}`);

  let response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (response.status === 401 && retry && await refreshAccessToken()) {
    return apiFetch(path, options, false);
  }
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      message = data.detail || Object.values(data).flat().join(' ') || message;
    } catch (_) {}
    throw new Error(message);
  }
  if (response.status === 204) return null;
  return response.json();
}

export { API_BASE };
