const { STORAGE_KEYS, setItem, getItem, clearSession, removeItem } = require('../utils/storage');

function pickStr(obj, camel, snake) {
  const v = obj[camel] != null ? obj[camel] : obj[snake];
  return typeof v === 'string' ? v : v != null ? String(v) : '';
}

function pickNum(obj, camel, snake) {
  const v = obj[camel] != null ? obj[camel] : obj[snake];
  return typeof v === 'number' ? v : Number(v) || 0;
}

/** 将登录响应统一为 camelCase，兼容 snake_case */
function normalizeLoginResponse(raw) {
  const data = raw || {};

  if (Array.isArray(data.tenants)) {
    const tenants = data.tenants.map((t) => ({
      tenantCode: pickStr(t, 'tenantCode', 'tenant_code'),
      tenantName: pickStr(t, 'tenantName', 'tenant_name')
    }));
    return {
      needSelectTenant: data.needSelectTenant !== false,
      tenants
    };
  }

  const userRaw = data.user || {};
  const roles = userRaw.roles;
  const user = {
    userId: pickNum(userRaw, 'userId', 'user_id'),
    phone: pickStr(userRaw, 'phone', 'phone'),
    realName: pickStr(userRaw, 'realName', 'real_name') || undefined,
    avatar: pickStr(userRaw, 'avatar', 'avatar') || undefined,
    tenantCode: pickStr(userRaw, 'tenantCode', 'tenant_code') || undefined,
    tenantName: pickStr(userRaw, 'tenantName', 'tenant_name') || undefined,
    forceChangePwd: pickNum(userRaw, 'forceChangePwd', 'force_change_pwd'),
    roles: Array.isArray(roles) ? roles : [],
    permissions: Array.isArray(userRaw.permissions) ? userRaw.permissions : []
  };

  return {
    accessToken: pickStr(data, 'accessToken', 'access_token'),
    refreshToken: pickStr(data, 'refreshToken', 'refresh_token'),
    user
  };
}

function isMultiTenant(result) {
  return !!(result && Array.isArray(result.tenants));
}

function applyLoginSuccess(result) {
  setItem(STORAGE_KEYS.ACCESS_TOKEN, result.accessToken);
  setItem(STORAGE_KEYS.REFRESH_TOKEN, result.refreshToken || '');
  setItem(STORAGE_KEYS.USER_INFO, result.user);
  if (result.user && result.user.tenantCode) {
    setItem(STORAGE_KEYS.TENANT_CODE, result.user.tenantCode);
  }
  removeItem(STORAGE_KEYS.PENDING_LOGIN);

  const app = getApp();
  if (app) {
    app.globalData.userInfo = result.user;
    app.globalData.tenantCode = result.user.tenantCode || '';
  }
}

function savePendingLogin(creds) {
  setItem(STORAGE_KEYS.PENDING_LOGIN, creds);
}

function loadPendingLogin() {
  return getItem(STORAGE_KEYS.PENDING_LOGIN, null);
}

function clearPendingLogin() {
  removeItem(STORAGE_KEYS.PENDING_LOGIN);
}

function logout() {
  clearSession();
  const app = getApp();
  if (app) {
    app.globalData.userInfo = null;
    app.globalData.tenantCode = '';
  }
}

function getUserInfo() {
  return getItem(STORAGE_KEYS.USER_INFO, null);
}

function getTenantCode() {
  return getItem(STORAGE_KEYS.TENANT_CODE, '');
}

/** 登录成功后的统一跳转 */
function navigateAfterLogin(user) {
  wx.showToast({ title: '登录成功', icon: 'success', duration: 1200 });
  setTimeout(() => {
    if (user && Number(user.forceChangePwd) === 1) {
      wx.reLaunch({ url: '/pages/profile/change-password?force=1' });
      return;
    }
    wx.switchTab({ url: '/pages/home/index' });
  }, 400);
}

module.exports = {
  normalizeLoginResponse,
  isMultiTenant,
  applyLoginSuccess,
  savePendingLogin,
  loadPendingLogin,
  clearPendingLogin,
  logout,
  getUserInfo,
  getTenantCode,
  navigateAfterLogin
};
