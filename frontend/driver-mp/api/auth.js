const { get, post, put, openPost } = require('../utils/request');
const {
  normalizeLoginResponse,
  isMultiTenant,
  applyLoginSuccess,
  savePendingLogin,
  navigateAfterLogin
} = require('../services/session');

async function loginByPassword(payload) {
  const raw = await post('/auth/login', {
    phone: payload.phone,
    password: payload.password,
    tenant_code: payload.tenantCode
  });
  return normalizeLoginResponse(raw);
}

async function loginBySms(payload) {
  const raw = await post('/auth/sms-login', {
    phone: payload.phone,
    code: payload.code,
    tenant_code: payload.tenantCode
  });
  return normalizeLoginResponse(raw);
}

async function refreshToken(refreshTokenValue) {
  const raw = await post('/auth/refresh', {
    refresh_token: refreshTokenValue
  });
  return normalizeLoginResponse(raw);
}

function getUserInfoApi() {
  return get('/auth/user-info');
}

function getUserTenants() {
  return get('/auth/user-tenants');
}

async function switchTenant(tenantCode) {
  const raw = await post('/auth/switch-tenant', {
    tenant_code: tenantCode
  });
  return normalizeLoginResponse(raw);
}

function changePassword(payload) {
  return put('/auth/password', {
    oldPassword: payload.oldPassword,
    newPassword: payload.newPassword
  });
}

function sendSmsCode(payload) {
  return openPost('/sms/send', {
    phone: payload.phone,
    purpose: payload.purpose,
    app_type: 'client'
  });
}

/**
 * 处理登录结果：多企业 → 选企业页；单企业 → 落会话并跳转
 */
function handleLoginResult(result, creds) {
  if (isMultiTenant(result)) {
    savePendingLogin(creds);
    const app = getApp();
    if (app) {
      app.globalData.pendingTenants = result.tenants || [];
    }
    wx.navigateTo({ url: '/pages/tenant-select/tenant-select' });
    return;
  }
  applyLoginSuccess(result);
  navigateAfterLogin(result.user);
}

module.exports = {
  loginByPassword,
  loginBySms,
  refreshToken,
  getUserInfoApi,
  getUserTenants,
  switchTenant,
  changePassword,
  sendSmsCode,
  handleLoginResult
};
