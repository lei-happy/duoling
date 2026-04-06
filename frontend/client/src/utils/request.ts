/**
 * 请求工具
 */
import axios from 'axios';
import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { unref } from 'vue';
import { LOGIN_PATH, LAYOUT_PATH, TOKEN_HEADER_NAME } from '@/config/setting';
import type { ApiResult } from '@/api';
import router from '@/router';
import { isWhiteList } from '@/router/routes';
import { getToken, setToken, getRefreshToken, setRefreshToken, removeRefreshToken, isRememberToken } from './token-util';
import { goLogin, showExpiredLogout, toURLSearch } from './common';

/** 是否正在刷新token */
let isRefreshing = false;
/** 等待刷新token的请求队列 */
let pendingRequests: Array<{
  resolve: (token: string) => void;
  reject: (error: any) => void;
}> = [];

/**
 * 处理等待队列中的请求
 */
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

/**
 * 使用 refresh token 刷新 access token
 */
async function doRefreshToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return null;
  }
  try {
    const res = await axios.post<ApiResult<any>>(
      `${import.meta.env.VITE_API_URL}/auth/refresh`,
      { refresh_token: refreshToken }
    );
    if (res.data?.code === 0 && res.data.data) {
      const { access_token, refresh_token } = res.data.data;
      const remember = isRememberToken();
      setToken(access_token, remember);
      setRefreshToken(refresh_token, remember);
      return access_token;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * 请求拦截处理
 */
export function requestInterceptor(config: InternalAxiosRequestConfig<any>) {
  // 添加token到header
  const token = getToken();
  if (token && config.headers) {
    config.headers[TOKEN_HEADER_NAME] = `Bearer ${token}`;
  }

  // get请求处理数组和对象类型参数
  if (config.method === 'get' && config.params) {
    config.url = toURLSearch(config.params, config.url);
    config.params = {};
  }

  return config;
}

/**
 * 处理401未授权响应，尝试刷新token
 * @returns 新的token，或null（刷新失败）
 */
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

/**
 * 跳转到登录页
 */
function redirectToLogin(toRoute?: any) {
  const { path, fullPath } = toRoute || unref(router.currentRoute);
  if (!isWhiteList(path)) {
    if (path == LAYOUT_PATH || toRoute) {
      goLogin(path == LAYOUT_PATH ? void 0 : fullPath, true);
    } else if (path !== LOGIN_PATH) {
      showExpiredLogout(fullPath);
    }
  }
}

/**
 * 响应拦截处理
 */
export function responseInterceptor(res: AxiosResponse<ApiResult<unknown>>) {
  // 非401直接返回
  if (res.data?.code !== 401 && !(res.data?.code === 403 && !getToken())) {
    return;
  }
  // 401 由上层拦截器通过 refresh 逻辑处理
  return res.data.message;
}

/** 从 axios 错误响应体取后端 message（如登录失败时的业务提示） */
function getAxiosErrorServerMessage(error: unknown): string | undefined {
  const data = (error as any)?.response?.data as ApiResult<unknown> | undefined;
  const m = data?.message;
  return typeof m === 'string' && m.trim() ? m : undefined;
}

/**
 * 错误信息处理
 */
export function getErrorMessage(message: string) {
  if (message == 'Network Error') {
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

/** 创建axios实例 */
const service = axios.create({
  baseURL: import.meta.env.VITE_API_URL
});

/**
 * 添加响应拦截器
 */
service.interceptors.response.use(
  async (res: AxiosResponse<ApiResult<unknown>>) => {
    // 检测业务码401/403过期
    if (res.data?.code === 401 || (res.data?.code === 403 && !getToken())) {
      const toRoute = (res.config as any).toRoute;
      if ((res.config as any)._retried) {
        redirectToLogin(toRoute);
        return Promise.reject(new Error(res.data.message));
      }

      const newToken = await handleUnauthorized();
      if (newToken) {
        const config = res.config;
        config.headers[TOKEN_HEADER_NAME] = `Bearer ${newToken}`;
        (config as any)._retried = true;
        return service(config);
      }

      removeRefreshToken();
      redirectToLogin(toRoute);
      return Promise.reject(new Error(res.data.message));
    }

    return res;
  },
  async (error) => {
    // 处理 HTTP 401 状态码（token过期）
    if (error.response?.status === 401) {
      const config = error.config;
      const toRoute = config?.toRoute;

      if (config?._retried) {
        redirectToLogin(toRoute);
        return Promise.reject(
          new Error(getAxiosErrorServerMessage(error) || error.message)
        );
      }

      const newToken = await handleUnauthorized();
      if (newToken) {
        config.headers[TOKEN_HEADER_NAME] = `Bearer ${newToken}`;
        config._retried = true;
        return service(config);
      }

      removeRefreshToken();
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

/**
 * 添加请求拦截器
 */
service.interceptors.request.use(
  (config) => {
    return requestInterceptor(config);
  },
  (error) => {
    console.error(error);
    return Promise.reject(new Error(getErrorMessage(error.message)));
  }
);

export default service;
