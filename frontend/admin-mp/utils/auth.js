const { STORAGE_KEYS, getItem } = require('./storage');

function isLoggedIn() {
  return !!getItem(STORAGE_KEYS.TOKEN, '');
}

/**
 * @param {{ noAuth?: boolean }} options noAuth=true 表示登录页等无需鉴权
 */
function ensureAuth(options = {}) {
  const { noAuth = false } = options;
  if (noAuth) {
    if (isLoggedIn()) {
      wx.switchTab({ url: '/pages/home/index' });
    }
    return true;
  }
  if (!isLoggedIn()) {
    wx.reLaunch({ url: '/pages/login/login' });
    return false;
  }
  return true;
}

module.exports = {
  isLoggedIn,
  ensureAuth
};
