const { get, post, put } = require('../utils/request');
const { STORAGE_KEYS, getItem } = require('../utils/storage');
const {
  normalizeLoginResponse,
  isMultiTenant,
  applyLoginSuccess,
  mergeUserInfo,
  patchWorkplaceConfig
} = require('../utils/session');

async function loginByPassword({ phone, password, tenantCode }) {
  const payload = { phone, password };
  if (tenantCode) {
    payload.tenant_code = tenantCode;
  }
  const raw = await post('/auth/login', payload);
  return normalizeLoginResponse(raw);
}

async function fetchUserInfo() {
  const info = await get('/auth/user-info');
  return mergeUserInfo(info || {});
}

async function saveDefaultPersona(persona) {
  const user = getItem(STORAGE_KEYS.USER_INFO, {}) || {};
  const current =
    user.workplaceConfig && typeof user.workplaceConfig === 'object'
      ? user.workplaceConfig
      : {};
  const workplaceConfig = { ...current, defaultPersona: persona };
  await put('/auth/user-workplace-config', { workplaceConfig });
  patchWorkplaceConfig({ defaultPersona: persona });
  return workplaceConfig;
}

async function completeLogin(result) {
  applyLoginSuccess(result);
  return fetchUserInfo();
}

module.exports = {
  loginByPassword,
  fetchUserInfo,
  saveDefaultPersona,
  completeLogin,
  isMultiTenant
};
