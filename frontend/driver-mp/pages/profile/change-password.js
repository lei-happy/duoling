const { ensureAuth } = require('../../utils/auth');
const { changePassword } = require('../../api/auth');
const { STORAGE_KEYS, getItem, setItem } = require('../../utils/storage');
const { toast } = require('../../utils/request');

Page({
  data: {
    force: false,
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
    loading: false
  },

  onLoad(query) {
    this.setData({ force: query.force === '1' });
  },

  onShow() {
    ensureAuth({ allowForcePwd: true });
  },

  onOld(e) {
    this.setData({ oldPassword: e.detail.value || '' });
  },
  onNew(e) {
    this.setData({ newPassword: e.detail.value || '' });
  },
  onConfirm(e) {
    this.setData({ confirmPassword: e.detail.value || '' });
  },

  async onSubmit() {
    const { oldPassword, newPassword, confirmPassword, loading } = this.data;
    if (loading) return;
    if (!oldPassword) {
      toast('请输入原密码');
      return;
    }
    if (!newPassword || newPassword.length < 6) {
      toast('新密码至少 6 位');
      return;
    }
    if (newPassword !== confirmPassword) {
      toast('两次输入的新密码不一致');
      return;
    }
    this.setData({ loading: true });
    wx.showLoading({ title: '正在修改密码，请稍候…', mask: true });
    try {
      await changePassword({ oldPassword, newPassword });
      const user = getItem(STORAGE_KEYS.USER_INFO, null) || {};
      user.forceChangePwd = 0;
      setItem(STORAGE_KEYS.USER_INFO, user);
      const app = getApp();
      if (app) app.globalData.userInfo = user;
      toast('密码已修改');
      setTimeout(() => {
        wx.switchTab({ url: '/pages/home/index' });
      }, 500);
    } catch (e) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  }
});
