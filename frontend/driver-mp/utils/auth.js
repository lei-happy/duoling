const { STORAGE_KEYS, getItem } = require('./storage');

/**
 * 页面鉴权：与 H5 路由守卫对齐
 * - noAuth：登录页等
 * - requireTokenOnly：仅需 token（选企业）
 * - 默认：需 token + tenant；forceChangePwd 强制改密
 *
 * @returns {boolean} 是否已放行（false 表示已跳转）
 */
function ensureAuth(options) {
  const opts = options || {};
  const token = getItem(STORAGE_KEYS.ACCESS_TOKEN, '');
  const tenantCode = getItem(STORAGE_KEYS.TENANT_CODE, '');
  const userInfo = getItem(STORAGE_KEYS.USER_INFO, null);

  if (opts.noAuth) {
    if (token && tenantCode && !opts.allowWhenLoggedIn) {
      wx.switchTab({ url: '/pages/home/index' });
      return false;
    }
    return true;
  }

  if (!token) {
    wx.reLaunch({ url: '/pages/login/login' });
    return false;
  }

  if (opts.requireTokenOnly) {
    return true;
  }

  if (!tenantCode) {
    // 多企业第一步选企业不依赖 token；已登录却无 tenant 时回登录重走
    wx.reLaunch({ url: '/pages/login/login' });
    return false;
  }

  if (userInfo && Number(userInfo.forceChangePwd) === 1 && !opts.allowForcePwd) {
    const pages = getCurrentPages();
    const cur = pages[pages.length - 1];
    if (!cur || cur.route !== 'pages/profile/change-password') {
      wx.reLaunch({ url: '/pages/profile/change-password?force=1' });
      return false;
    }
  }

  return true;
}

function isLoggedIn() {
  return !!getItem(STORAGE_KEYS.ACCESS_TOKEN, '');
}

module.exports = {
  ensureAuth,
  isLoggedIn
};
