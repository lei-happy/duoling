import axios, { type AxiosInstance, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';
import { showToast, showFailToast } from 'vant';
import { getItem, removeItem, setItem, STORAGE_KEYS } from '@/utils/storage';

export interface ApiResponse<T = unknown> {
  code: number;
  message?: string;
  data?: T;
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
      const msg = body.message || '请求失败';
      showFailToast(msg);
      return Promise.reject(new Error(msg));
    }
    return resp;
  },
  (error) => {
    const status = error?.response?.status;
    const body = error?.response?.data;
    const msg = body?.message || error?.message || '网络异常';

    if (status === 401) {
      removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      removeItem(STORAGE_KEYS.USER_INFO);
      removeItem(STORAGE_KEYS.TENANT_CODE);
      showToast('登录已过期，请重新登录');
      if (window.location.pathname !== '/login') {
        const redirect = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/login?redirect=${redirect}`;
      }
    } else if (status === 403) {
      showFailToast('无权限访问');
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
