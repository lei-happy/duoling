/**
 * 请求工具 — 基于 @zhitu/shared-utils 的 createRequest 工厂函数
 */
import { unref } from 'vue';
import { createRequest } from '@zhitu/shared-utils';
import { LOGIN_PATH, LAYOUT_PATH, TOKEN_HEADER_NAME } from '@/config/setting';
import router from '@/router';
import { isWhiteList } from '@/router/routes';
import {
  getToken,
  setToken,
  getRefreshToken,
  setRefreshToken,
  removeRefreshToken,
  isRememberToken
} from './token-util';
import { goLogin, showExpiredLogout, toURLSearch } from './common';

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

const service = createRequest({
  baseURL: import.meta.env.VITE_API_URL,
  tokenHeaderName: TOKEN_HEADER_NAME,
  getToken,
  setToken,
  getRefreshToken,
  setRefreshToken,
  removeRefreshToken,
  isRememberToken,
  redirectToLogin,
  toURLSearch
});

export default service;
