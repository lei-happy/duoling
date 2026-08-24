const STORAGE_KEYS = {
  TOKEN: 'admin_mp_token',
  REFRESH_TOKEN: 'admin_mp_refresh_token',
  USER_INFO: 'admin_mp_user_info',
  TENANT_CODE: 'admin_mp_tenant_code',
  PENDING_TENANTS: 'admin_mp_pending_tenants',
  PENDING_LOGIN: 'admin_mp_pending_login'
};

function getItem(key, fallback) {
  try {
    const v = wx.getStorageSync(key);
    return v === '' || v === undefined || v === null ? fallback : v;
  } catch (e) {
    return fallback;
  }
}

function setItem(key, value) {
  wx.setStorageSync(key, value);
}

function removeItem(key) {
  try {
    wx.removeStorageSync(key);
  } catch (e) {
    /* ignore */
  }
}

function clearSession() {
  removeItem(STORAGE_KEYS.TOKEN);
  removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  removeItem(STORAGE_KEYS.USER_INFO);
  removeItem(STORAGE_KEYS.TENANT_CODE);
  removeItem(STORAGE_KEYS.PENDING_TENANTS);
  removeItem(STORAGE_KEYS.PENDING_LOGIN);
}

module.exports = {
  STORAGE_KEYS,
  getItem,
  setItem,
  removeItem,
  clearSession
};
