const { STORAGE_KEYS, getItem, setItem, removeItem } = require('./storage');

function pickStr(obj, camel, snake) {
  if (!obj) return '';
  const v = obj[camel] != null ? obj[camel] : obj[snake];
  return typeof v === 'string' ? v : v != null ? String(v) : '';
}

function pickNum(obj, camel, snake) {
  if (!obj) return 0;
  const v = obj[camel] != null ? obj[camel] : obj[snake];
  return typeof v === 'number' ? v : Number(v) || 0;
}

function normalizeLoginResponse(raw) {
  const data = raw || {};
  if (Array.isArray(data.tenants)) {
    return {
      needSelectTenant: data.needSelectTenant !== false,
      tenants: data.tenants.map((t) => ({
        tenantCode: pickStr(t, 'tenantCode', 'tenant_code'),
        tenantName: pickStr(t, 'tenantName', 'tenant_name')
      }))
    };
  }

  const userRaw = data.user || {};
  return {
    accessToken: pickStr(data, 'accessToken', 'access_token'),
    refreshToken: pickStr(data, 'refreshToken', 'refresh_token'),
    user: {
      userId: pickNum(userRaw, 'userId', 'user_id'),
      phone: pickStr(userRaw, 'phone', 'phone'),
      realName: pickStr(userRaw, 'realName', 'real_name'),
      tenantCode: pickStr(userRaw, 'tenantCode', 'tenant_code'),
      userType: pickNum(userRaw, 'userType', 'user_type'),
      roles: Array.isArray(userRaw.roles) ? userRaw.roles : []
    }
  };
}

function isMultiTenant(result) {
  return !!(result && Array.isArray(result.tenants));
}

function applyLoginSuccess(result) {
  setItem(STORAGE_KEYS.TOKEN, result.accessToken);
  if (result.refreshToken) {
    setItem(STORAGE_KEYS.REFRESH_TOKEN, result.refreshToken);
  }
  setItem(STORAGE_KEYS.USER_INFO, result.user);
  if (result.user && result.user.tenantCode) {
    setItem(STORAGE_KEYS.TENANT_CODE, result.user.tenantCode);
  }
  const app = getApp();
  if (app) {
    app.globalData.userInfo = result.user;
    app.globalData.tenantCode = (result.user && result.user.tenantCode) || '';
  }
}

function mergeUserInfo(info) {
  const current = getItem(STORAGE_KEYS.USER_INFO, {}) || {};
  const merged = {
    ...current,
    realName: info.nickname || current.realName || '',
    phone: info.phone || current.phone || '',
    userType: info.userType != null ? info.userType : current.userType,
    roles: Array.isArray(info.roles) ? info.roles : current.roles || [],
    personas: Array.isArray(info.personas) ? info.personas : [],
    authorities: Array.isArray(info.authorities) ? info.authorities : [],
    features: Array.isArray(info.features) ? info.features : current.features || [],
    workplaceConfig: info.workplaceConfig || current.workplaceConfig || {},
    tenantName: info.tenantName || current.tenantName || '',
    tenantCode: info.tenantCode || current.tenantCode || getItem(STORAGE_KEYS.TENANT_CODE, '') || ''
  };
  setItem(STORAGE_KEYS.USER_INFO, merged);
  const app = getApp();
  if (app) {
    app.globalData.userInfo = merged;
  }
  return merged;
}

function patchWorkplaceConfig(patch) {
  const user = getItem(STORAGE_KEYS.USER_INFO, {}) || {};
  const current =
    user.workplaceConfig && typeof user.workplaceConfig === 'object'
      ? { ...user.workplaceConfig }
      : {};
  const next = { ...current, ...patch };
  const merged = { ...user, workplaceConfig: next };
  setItem(STORAGE_KEYS.USER_INFO, merged);
  const app = getApp();
  if (app) {
    app.globalData.userInfo = merged;
  }
  return next;
}

function clearPendingTenants() {
  removeItem(STORAGE_KEYS.PENDING_TENANTS);
}

module.exports = {
  normalizeLoginResponse,
  isMultiTenant,
  applyLoginSuccess,
  mergeUserInfo,
  patchWorkplaceConfig,
  clearPendingTenants
};
