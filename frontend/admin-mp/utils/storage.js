const STORAGE_KEYS = {
  TOKEN: 'admin_mp_token',
  USER_INFO: 'admin_mp_user_info',
  TENANT_CODE: 'admin_mp_tenant_code'
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
  removeItem(STORAGE_KEYS.USER_INFO);
  removeItem(STORAGE_KEYS.TENANT_CODE);
}

module.exports = {
  STORAGE_KEYS,
  getItem,
  setItem,
  removeItem,
  clearSession
};
