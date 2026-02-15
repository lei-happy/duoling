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
import { getToken, setToken } from './token-util';
import { goLogin, showExpiredLogout, toURLSearch } from './common';

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
 * 响应拦截处理
 */
export function responseInterceptor(res: AxiosResponse<ApiResult<unknown>>) {
  // 登录过期处理
  if (res.data?.code === 401 || (res.data?.code === 403 && !getToken())) {
    const toRoute = (res.config as any).toRoute;
    const { path, fullPath } = toRoute || unref(router.currentRoute);
    if (!isWhiteList(path)) {
      if (path == LAYOUT_PATH || toRoute) {
        goLogin(path == LAYOUT_PATH ? void 0 : fullPath, true);
      } else if (path !== LOGIN_PATH) {
        showExpiredLogout(fullPath);
      }
    }
    return res.data.message;
  }
  // 续期token
  const newToken = res.headers['authorization'];
  if (newToken) {
    setToken(newToken);
  }
}

/**
 * 错误信息处理
 */
export function getErrorMessage(message) {
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
  (res: AxiosResponse<ApiResult<unknown>>) => {
    const errorMessage = responseInterceptor(res);
    if (errorMessage) {
      return Promise.reject(new Error(errorMessage));
    }
    return res;
  },
  (error) => {
    console.error(error);
    return Promise.reject(new Error(getErrorMessage(error.message)));
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
