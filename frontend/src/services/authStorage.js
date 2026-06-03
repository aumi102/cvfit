export const AUTH_TOKEN_STORAGE_KEY = 'auth_token';
export const AUTH_USER_STORAGE_KEY = 'user';

function isBrowser() {
  return typeof window !== 'undefined';
}

function looksLikeJwt(token) {
  return typeof token === 'string' && token.split('.').length === 3;
}

export function getStoredAuthToken() {
  if (!isBrowser()) {
    return null;
  }
  const token = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
  if (!token || !looksLikeJwt(token)) {
    localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
    return null;
  }
  return token;
}

export function safeUser(user) {
  if (!user) {
    return null;
  }
  return {
    id: user.id,
    email: user.email,
    full_name: user.full_name || null,
    is_active: Boolean(user.is_active),
  };
}

export function storeAuthSession(authResponse) {
  if (!isBrowser()) {
    return null;
  }
  const token = authResponse?.access_token;
  const user = safeUser(authResponse?.user);
  if (!token || !user) {
    throw new Error('Invalid authentication response.');
  }
  localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token);
  localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(user));
  return user;
}

export function storeSafeUser(user) {
  if (!isBrowser()) {
    return null;
  }
  const normalized = safeUser(user);
  if (!normalized) {
    return null;
  }
  localStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(normalized));
  return normalized;
}

export function getStoredUser() {
  if (!isBrowser()) {
    return null;
  }
  try {
    const raw = localStorage.getItem(AUTH_USER_STORAGE_KEY);
    return raw ? safeUser(JSON.parse(raw)) : null;
  } catch {
    localStorage.removeItem(AUTH_USER_STORAGE_KEY);
    return null;
  }
}

export function clearAuthSession() {
  if (!isBrowser()) {
    return;
  }
  localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
  localStorage.removeItem(AUTH_USER_STORAGE_KEY);
}
