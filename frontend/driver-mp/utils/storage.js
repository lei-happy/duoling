const PREFIX = 'zt_driver_';

const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_INFO: 'user_info',
  TENANT_CODE: 'tenant_code',
  TENANT_LIST: 'tenant_list',
  PENDING_LOGIN: 'pending_login'
};

function setItem(key, value) {
  try {
    wx.setStorageSync(PREFIX + key, value);
  } catch (e) {
    /* ignore */
  }
}

function getItem(key, defaultValue) {
  try {
    const v = wx.getStorageSync(PREFIX + key);
    return v === '' || v === undefined || v === null ? defaultValue : v;
  } catch (e) {
    return defaultValue;
  }
}

function removeItem(key) {
  try {
    wx.removeStorageSync(PREFIX + key);
  } catch (e) {
    /* ignore */
  }
}

function clearSession() {
  removeItem(STORAGE_KEYS.ACCESS_TOKEN);
  removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  removeItem(STORAGE_KEYS.USER_INFO);
  removeItem(STORAGE_KEYS.TENANT_CODE);
  removeItem(STORAGE_KEYS.TENANT_LIST);
  removeItem(STORAGE_KEYS.PENDING_LOGIN);
}

module.exports = {
  STORAGE_KEYS,
  setItem,
  getItem,
  removeItem,
  clearSession
};
