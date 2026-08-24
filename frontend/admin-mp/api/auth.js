const { get, post, put } = require('../utils/request');
const { STORAGE_KEYS, getItem } = require('../utils/storage');
const {
  normalizeLoginResponse,
  isMultiTenant,
  applyLoginSuccess,
  mergeUserInfo,
  patchWorkplaceConfig
} = require('../utils/session');
const { resolvePersona } = require('../utils/persona');

async function loginByPassword({ phone, password, tenantCode }) {
  const payload = { phone, password };
  if (tenantCode) payload.tenant_code = tenantCode;
  return normalizeLoginResponse(await post('/auth/login', payload));
}

async function sendSmsCode(phone) {
  return post(
    '/sms/send',
    { phone, purpose: 1, app_type: 'client' },
    { base: 'open' }
  );
}

async function loginBySms({ phone, code, tenantCode }) {
  const payload = { phone, code };
  if (tenantCode) payload.tenant_code = tenantCode;
  return normalizeLoginResponse(await post('/auth/sms-login', payload));
}

async function fetchUserInfo() {
  return mergeUserInfo((await get('/auth/user-info')) || {});
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

function goAfterLogin(user) {
  const personas = (user && user.personas) || [];
  const preferred = user && user.workplaceConfig && user.workplaceConfig.defaultPersona;
  if (personas.length > 1 && !preferred) {
    wx.redirectTo({ url: '/pages/persona-select/index' });
    return;
  }
  wx.switchTab({ url: '/pages/home/index' });
}

async function finishLogin(result) {
  const user = await completeLogin(result);
  goAfterLogin(user);
  return user;
}

async function listTenants() {
  return get('/auth/user-tenants');
}

async function switchTenant(tenantCode) {
  const raw = await post('/auth/switch-tenant', { tenant_code: tenantCode });
  const result = normalizeLoginResponse(raw);
  if (result.accessToken) {
    applyLoginSuccess(result);
    return fetchUserInfo();
  }
  return result;
}

async function changePassword({ oldPassword, newPassword }) {
  return put('/auth/password', { oldPassword, newPassword });
}

function canSeeFinance(user) {
  if (!user) return false;
  if (Number(user.userType) === 1) return true;
  const feats = user.features || [];
  if (feats.some((f) => /finance/i.test(String(f)))) return true;
  return resolvePersona(user) === 'finance';
}

module.exports = {
  loginByPassword,
  loginBySms,
  sendSmsCode,
  fetchUserInfo,
  saveDefaultPersona,
  completeLogin,
  finishLogin,
  goAfterLogin,
  listTenants,
  switchTenant,
  changePassword,
  canSeeFinance,
  isMultiTenant
};
