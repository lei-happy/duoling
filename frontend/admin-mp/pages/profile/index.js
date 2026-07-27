const { ensureAuth } = require('../../utils/auth');
const { STORAGE_KEYS, getItem, clearSession } = require('../../utils/storage');

function maskPhone(phone) {
  if (!phone || phone.length < 7) return phone || '-';
  return `${phone.slice(0, 3)}****${phone.slice(-4)}`;
}

Page({
  data: {
    realName: '',
    phoneMasked: '',
    roles: []
  },

  onShow() {
    if (!ensureAuth()) return;
    const user = getItem(STORAGE_KEYS.USER_INFO, null) || {};
    this.setData({
      realName: user.realName || user.name || '管理员',
      phoneMasked: maskPhone(user.phone),
      roles: user.roles || ['管理员']
    });
  },

  onAbout() {
    wx.showModal({
      title: '关于',
      content: '智途管理员小程序脚手架（TDesign）。面向老板、财务、调度等角色的手机端能力将逐步上线。',
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
