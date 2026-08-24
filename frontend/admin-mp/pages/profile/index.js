const { ensureAuth } = require('../../utils/auth');
const { STORAGE_KEYS, getItem, clearSession } = require('../../utils/storage');
const { personaLabel } = require('../../utils/persona');

function maskPhone(phone) {
  if (!phone || phone.length < 7) return phone || '-';
  return `${phone.slice(0, 3)}****${phone.slice(-4)}`;
}

function roleLabels(user) {
  const roles = (user && user.roles) || [];
  const names = roles
    .map((item) => {
      if (typeof item === 'string') return item;
      return item.roleName || '';
    })
    .filter(Boolean);
  if (names.length) return names;
  return ['管理员'];
}

function personaTags(user) {
  return ((user && user.personas) || []).map(personaLabel).filter(Boolean);
}

Page({
  data: {
    realName: '',
    phoneMasked: '',
    roles: [],
    personas: []
  },

  onShow() {
    if (!ensureAuth()) return;
    const user = getItem(STORAGE_KEYS.USER_INFO, null) || {};
    this.setData({
      realName: user.realName || user.nickname || user.name || '管理员',
      phoneMasked: maskPhone(user.phone),
      roles: roleLabels(user),
      personas: personaTags(user)
    });
  },

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
      content: '确定退出当前账号吗？',
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
