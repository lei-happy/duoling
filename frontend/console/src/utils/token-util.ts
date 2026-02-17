/**
 * token操作封装
 */
import { TOKEN_CACHE_NAME, REFRESH_TOKEN_CACHE_NAME } from '@/config/setting';

/**
 * 获取缓存的token
 */
export function getToken(): string | null {
  const token = localStorage.getItem(TOKEN_CACHE_NAME);
  if (!token) {
    return sessionStorage.getItem(TOKEN_CACHE_NAME);
  }
  return token;
}

/**
 * 缓存token
 * @param token token
 * @param remember 是否永久存储
 */
export function setToken(token?: string, remember?: boolean) {
  removeToken();
  if (token) {
    if (remember) {
      localStorage.setItem(TOKEN_CACHE_NAME, token);
    } else {
      sessionStorage.setItem(TOKEN_CACHE_NAME, token);
    }
  }
}

/**
 * 移除token
 */
export function removeToken() {
  localStorage.removeItem(TOKEN_CACHE_NAME);
  sessionStorage.removeItem(TOKEN_CACHE_NAME);
}

/**
 * 获取缓存的refresh token
 */
export function getRefreshToken(): string | null {
  const token = localStorage.getItem(REFRESH_TOKEN_CACHE_NAME);
  if (!token) {
    return sessionStorage.getItem(REFRESH_TOKEN_CACHE_NAME);
  }
  return token;
}

/**
 * 缓存refresh token
 * @param token refresh token
 * @param remember 是否永久存储
 */
export function setRefreshToken(token?: string, remember?: boolean) {
  removeRefreshToken();
  if (token) {
    if (remember) {
      localStorage.setItem(REFRESH_TOKEN_CACHE_NAME, token);
    } else {
      sessionStorage.setItem(REFRESH_TOKEN_CACHE_NAME, token);
    }
  }
}

/**
 * 移除refresh token
 */
export function removeRefreshToken() {
  localStorage.removeItem(REFRESH_TOKEN_CACHE_NAME);
  sessionStorage.removeItem(REFRESH_TOKEN_CACHE_NAME);
}
