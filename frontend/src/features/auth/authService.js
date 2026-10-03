import { apiFetch, clearTokens, setTokens } from '../../api/client';

const normalizeUser = (user) => ({
  ...user,
  role: String(user.role || 'PATIENT').toLowerCase(),
  name: `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username,
});

export async function login(username, password) {
  const data = await apiFetch('/accounts/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  setTokens(data.access, data.refresh);
  const user = normalizeUser(data.user);
  localStorage.setItem('pillsync_user', JSON.stringify(user));
  return user;
}

export async function register({ username, email, password, firstName, lastName, phone, role }) {
  await apiFetch('/accounts/register/', {
    method: 'POST',
    body: JSON.stringify({
      username, email, password, first_name: firstName, last_name: lastName, phone, role: role?.toUpperCase(),
    }),
  });
  return login(username, password);
}

export async function currentUser() {
  const user = normalizeUser(await apiFetch('/accounts/me/'));
  localStorage.setItem('pillsync_user', JSON.stringify(user));
  return user;
}

export function logout() {
  clearTokens();
}
