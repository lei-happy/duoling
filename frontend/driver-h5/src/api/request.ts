import axios, { type AxiosInstance, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';
import { showToast, showFailToast } from 'vant';
import { getItem, removeItem, setItem, STORAGE_KEYS } from '@/utils/storage';

export interface ApiResponse<T = unknown> {
  code: number;
  message?: string;
  data?: T;
}

/** 登录/选企业相关接口：401 应展示后端业务文案，而非「登录已过期」 */
const AUTH_LOGIN_URLS = ['/auth/login', '/auth/sms-login', '/auth/switch-tenant'];

const AUTH_PAGE_PATHS = ['/login', '/sms-login', '/tenant-select'];

function isAuthLoginRequest(url?: string): boolean {
  if (!url) return false;
  return AUTH_LOGIN_URLS.some((p) => url.includes(p));
}

function isOnAuthPage(): boolean {
  const path = window.location.pathname || '';
  return AUTH_PAGE_PATHS.some((p) => path === p || path.endsWith(p));
}

const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/driver',
  timeout: 20000
});

request.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getItem<string>(STORAGE_KEYS.ACCESS_TOKEN, '');
  if (token) {
    config.headers = config.headers ?? {};
    (config.headers as Record<string, string>).Authorization = `Bearer ${token}`;
  }
  return config;
});

request.interceptors.response.use(
  (resp: AxiosResponse<ApiResponse>) => {
    const refreshed = resp.headers?.['authorization'] || resp.headers?.['Authorization'];
    if (typeof refreshed === 'string' && refreshed.startsWith('Bearer ')) {
      setItem(STORAGE_KEYS.ACCESS_TOKEN, refreshed.slice('Bearer '.length));
    }

    const body = resp.data;
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) return body as unknown as AxiosResponse;
      const msg = body.message || '操作失败，请稍后重试';
      showFailToast(msg);
      return Promise.reject(new Error(msg));
    }
    return resp;
  },
  (error) => {
    const status = error?.response?.status;
    const body = error?.response?.data;
    const msg = body?.message || error?.message || '加载失败，请重试';
    const reqUrl = error?.config?.url as string | undefined;
    const authLoginFail = isAuthLoginRequest(reqUrl) || isOnAuthPage();

    const sessionExpired =
      status === 401 ||
      Number(body?.code) === 401 ||
      (status === 400 && String(msg).includes('请确认登录状态'));

    if (sessionExpired) {
      if (authLoginFail) {
        // 登录/选企业失败：展示后端真实原因，不清会话、不整页跳转
        showFailToast(msg || '登录失败，请重试');
      } else {
        removeItem(STORAGE_KEYS.ACCESS_TOKEN);
        removeItem(STORAGE_KEYS.USER_INFO);
        removeItem(STORAGE_KEYS.TENANT_CODE);
        showToast('登录已过期，请重新登录');
        if (window.location.pathname !== '/login') {
          const redirect = encodeURIComponent(window.location.pathname + window.location.search);
          window.location.href = `/login?redirect=${redirect}`;
        }
      }
    } else if (status === 403) {
      showFailToast(authLoginFail ? msg || '无权限访问' : '无权限访问');
    } else {
      showFailToast(msg);
    }
    return Promise.reject(error);
  }
);

export default request;

export async function get<T = unknown>(url: string, params?: Record<string, unknown>): Promise<T> {
  const res = await request.get<ApiResponse<T>>(url, { params });
  return (res.data?.data ?? (res.data as unknown as T)) as T;
}

export async function post<T = unknown>(url: string, body?: unknown): Promise<T> {
  const res = await request.post<ApiResponse<T>>(url, body);
  return (res.data?.data ?? (res.data as unknown as T)) as T;
}

export async function put<T = unknown>(url: string, body?: unknown): Promise<T> {
  const res = await request.put<ApiResponse<T>>(url, body);
  return (res.data?.data ?? (res.data as unknown as T)) as T;
}

export async function del<T = unknown>(url: string, params?: Record<string, unknown>): Promise<T> {
  const res = await request.delete<ApiResponse<T>>(url, { params });
  return (res.data?.data ?? (res.data as unknown as T)) as T;
}
