/**
 * 统一 HTTP 请求封装
 *
 * 提供 createRequest 工厂函数，console 和 client 通过配置注入差异。
 * 统一处理：Token 注入、Token 刷新、业务码解包、错误消息。
 */
import axios from 'axios';
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import type { ApiResult } from '@zhitu/shared-types';

export interface RequestConfig {
  /** API 基础路径，如 /api/console */
  baseURL: string;
  /** Token 请求头名称 */
  tokenHeaderName: string;
  /** 获取当前 access token */
  getToken: () => string | null;
  /** 存储新 token */
  setToken: (token: string, remember: boolean) => void;
  /** 获取 refresh token */
  getRefreshToken: () => string | null;
  /** 存储新 refresh token */
  setRefreshToken: (token: string, remember: boolean) => void;
  /** 移除 refresh token */
  removeRefreshToken: () => void;
  /** 是否记住登录 */
  isRememberToken: () => boolean;
  /** 刷新 token 的接口路径（相对于 baseURL） */
  refreshTokenPath?: string;
  /** 跳转到登录页 */
  redirectToLogin: (toRoute?: any) => void;
  /** 参数序列化工具 */
  toURLSearch: (params: any, url?: string) => string;
}

let isRefreshing = false;
let pendingRequests: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

function processPendingRequests(token: string | null, error?: any) {
  pendingRequests.forEach(({ resolve, reject }) => {
    if (token) {
      resolve(token);
    } else {
      reject(error);
    }
  });
  pendingRequests = [];
}

export function getErrorMessage(message: string) {
  if (message === 'Network Error') {
    return '后端接口连接异常';
  }
  if (message.includes('timeout')) {
    return '系统接口请求超时';
  }
  if (message.includes('Request failed with status code')) {
    return `系统接口${message.substr(message.length - 3)}异常`;
  }
  return message;
}

function getAxiosErrorServerMessage(error: unknown): string | undefined {
  const data = (error as any)?.response?.data as ApiResult | undefined;
  const m = data?.message;
  return typeof m === 'string' && m.trim() ? m : undefined;
}

/**
 * 创建配置化的 axios 实例
 */
export function createRequest(config: RequestConfig): AxiosInstance {
  const {
    baseURL,
    tokenHeaderName,
    getToken,
    setToken,
    getRefreshToken: getRefresh,
    setRefreshToken: setRefresh,
    removeRefreshToken: removeRefresh,
    isRememberToken,
    refreshTokenPath = '/auth/refresh',
    redirectToLogin,
    toURLSearch,
  } = config;

  const service = axios.create({ baseURL });

  async function doRefreshToken(): Promise<string | null> {
    const refreshToken = getRefresh();
    if (!refreshToken) return null;
    try {
      const res = await axios.post<ApiResult<any>>(
        `${baseURL}${refreshTokenPath}`,
        { refresh_token: refreshToken }
      );
      if (res.data?.code === 0 && res.data.data) {
        const { access_token, refresh_token } = res.data.data;
        const remember = isRememberToken();
        setToken(access_token, remember);
        setRefresh(refresh_token, remember);
        return access_token;
      }
      return null;
    } catch {
      return null;
    }
  }

  function handleUnauthorized(): Promise<string | null> {
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingRequests.push({ resolve, reject });
      });
    }
    isRefreshing = true;
    return doRefreshToken()
      .then((newToken) => {
        processPendingRequests(newToken);
        return newToken;
      })
      .catch((error) => {
        processPendingRequests(null, error);
        return null;
      })
      .finally(() => {
        isRefreshing = false;
      });
  }

  service.interceptors.request.use(
    (reqConfig: InternalAxiosRequestConfig) => {
      const token = getToken();
      if (token && reqConfig.headers) {
        reqConfig.headers[tokenHeaderName] = `Bearer ${token}`;
      }
      if (reqConfig.method === 'get' && reqConfig.params) {
        reqConfig.url = toURLSearch(reqConfig.params, reqConfig.url);
        reqConfig.params = {};
      }
      return reqConfig;
    },
    (error) => {
      console.error(error);
      return Promise.reject(new Error(getErrorMessage(error.message)));
    }
  );

  service.interceptors.response.use(
    async (res: AxiosResponse<ApiResult>) => {
      if (res.data?.code === 401 || (res.data?.code === 403 && !getToken())) {
        const toRoute = (res.config as any).toRoute;
        if ((res.config as any)._retried) {
          redirectToLogin(toRoute);
          return Promise.reject(new Error(res.data.message));
        }
        const newToken = await handleUnauthorized();
        if (newToken) {
          const retryConfig = res.config;
          retryConfig.headers[tokenHeaderName] = `Bearer ${newToken}`;
          (retryConfig as any)._retried = true;
          return service(retryConfig);
        }
        removeRefresh();
        redirectToLogin(toRoute);
        return Promise.reject(new Error(res.data.message));
      }
      return res;
    },
    async (error) => {
      if (error.response?.status === 401) {
        const retryConfig = error.config;
        const toRoute = retryConfig?.toRoute;
        if (retryConfig?._retried) {
          redirectToLogin(toRoute);
          return Promise.reject(
            new Error(getAxiosErrorServerMessage(error) || error.message)
          );
        }
        const newToken = await handleUnauthorized();
        if (newToken) {
          retryConfig.headers[tokenHeaderName] = `Bearer ${newToken}`;
          retryConfig._retried = true;
          return service(retryConfig);
        }
        removeRefresh();
        redirectToLogin(toRoute);
        return Promise.reject(
          new Error(getAxiosErrorServerMessage(error) || error.message)
        );
      }
      console.error(error);
      const serverMsg = getAxiosErrorServerMessage(error);
      return Promise.reject(
        new Error(serverMsg || getErrorMessage((error as Error).message))
      );
    }
  );

  return service;
}
