const { ensureAuth } = require('../../utils/auth');
const { STORAGE_KEYS, getItem, clearSession } = require('../../utils/storage');
const { personaLabel } = require('../../utils/persona');
const { maskPhone } = require('../../utils/format');

function roleLabels(user) {
  const roles = (user && user.roles) || [];
  const names = roles
    .map((item) => (typeof item === 'string' ? item : item.roleName || ''))
    .filter(Boolean);
  return names.length ? names : ['管理员'];
}

Page({
  data: {
    realName: '',
    phoneMasked: '',
    tenantName: '',
    roles: [],
    personas: []
  },

  onShow() {
    if (!ensureAuth()) return;
    const user = getItem(STORAGE_KEYS.USER_INFO, null) || {};
    this.setData({
      realName: user.realName || user.nickname || '管理员',
      phoneMasked: maskPhone(user.phone),
      tenantName: user.tenantName || '',
      roles: roleLabels(user),
      personas: ((user.personas) || []).map(personaLabel).filter(Boolean)
    });
  },

  goSwitch() { wx.navigateTo({ url: '/pages/profile/switch-tenant' }); },
  goRoles() { wx.navigateTo({ url: '/pages/profile/roles' }); },
  goPassword() { wx.navigateTo({ url: '/pages/profile/password' }); },
  goLookup() { wx.navigateTo({ url: '/pages/lookup/index' }); },
  goNotify() { wx.navigateTo({ url: '/pages/message/notify' }); },

  onAbout() {
    wx.showModal({
      title: '关于',
      content: '智途管理员小程序。岗位视图只决定先看到什么，权限与电脑端一致。',
      showCancel: false
    });
  },

  onLogout() {
    wx.showModal({
      title: '退出登录',
      content: '退出后将收不到服务通知。确定退出吗？',
      success(res) {
        if (!res.confirm) return;
        clearSession();
        const app = getApp();
        if (app) {
          app.globalData.userInfo = null;
          app.globalData.tenantCode = '';
        }
        wx.reLaunch({ url: '/pages/login/login' });
      }
    });
  }
});
