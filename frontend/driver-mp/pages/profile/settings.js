const { ensureAuth } = require('../../utils/auth');
const { logout } = require('../../services/session');
const { getFontScale, setFontScale } = require('../../utils/font');
const { toast } = require('../../utils/request');

Page({
  data: {
    fontClass: 'font-lg',
    scale: 'large'
  },

  onShow() {
    if (!ensureAuth({})) return;
    const s = getFontScale();
    this.setData({ scale: s.key, fontClass: s.className });
  },

  onScale(e) {
    const key = e.currentTarget.dataset.v;
    const s = setFontScale(key);
    this.setData({ scale: s.key, fontClass: s.className });
    toast('字号已调整');
  },

  onClearCache() {
    toast('本地缓存不多，已整理完。登录状态还在。');
  },

  onAbout() {
    wx.showModal({
      title: '关于智途·司机端',
      content: '智途驾驶员小程序\n版本 v0.1.0\n\n有问题请联系企业管理员。',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  goPassword() {
    wx.navigateTo({ url: '/pages/profile/change-password' });
  },

  onLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出当前账号吗？',
      confirmText: '退出',
      confirmColor: '#07c160',
      success(res) {
        if (!res.confirm) return;
        logout();
        wx.reLaunch({ url: '/pages/login/login' });
      }
    });
  }
});
