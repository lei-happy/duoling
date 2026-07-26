const { ensureAuth } = require('../../utils/auth');
const { getUserInfo, getTenantCode, logout } = require('../../services/session');
const { maskPhone } = require('../../utils/format');

Page({
  data: {
    realName: '司机',
    avatarText: '司',
    phoneMasked: '',
    tenantName: '-'
  },

  onShow() {
    if (!ensureAuth({})) return;
    const user = getUserInfo() || {};
    const name = user.realName || '司机';
    this.setData({
      realName: name,
      avatarText: name.slice(0, 1),
      phoneMasked: maskPhone(user.phone),
      tenantName: user.tenantName || getTenantCode() || '-'
    });
  },

  goInfo() {
    wx.navigateTo({ url: '/pages/profile/info' });
  },

  goSwitchTenant() {
    wx.navigateTo({ url: '/pages/profile/switch-tenant' });
  },

  goChangePassword() {
    wx.navigateTo({ url: '/pages/profile/change-password' });
  },

  goSummary() {
    wx.navigateTo({ url: '/pages/finance/summary' });
  },

  onAbout() {
    wx.showModal({
      title: '关于智途·司机端',
      content: '智途驾驶员小程序\n版本 v0.1.0\n\n如有问题请联系企业管理员。',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  onLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出当前账号吗？',
      success(res) {
        if (!res.confirm) return;
        logout();
        wx.reLaunch({ url: '/pages/login/login' });
      }
    });
  }
});
