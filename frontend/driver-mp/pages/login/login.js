const { ensureAuth } = require('../../utils/auth');
const { loginByPassword, handleLoginResult } = require('../../api/auth');
const { toast } = require('../../utils/request');

Page({
  data: {
    phone: '',
    password: '',
    loading: false
  },

  onShow() {
    ensureAuth({ noAuth: true });
  },

  onPhone(e) {
    this.setData({ phone: (e.detail.value || '').trim() });
  },

  onPassword(e) {
    this.setData({ password: e.detail.value || '' });
  },

  async onSubmit() {
    const { phone, password, loading } = this.data;
    if (loading) return;
    if (!/^1\d{10}$/.test(phone)) {
      toast('请输入正确的手机号');
      return;
    }
    if (!password) {
      toast('请输入密码');
      return;
    }

    this.setData({ loading: true });
    wx.showLoading({ title: '正在登录，请稍候…', mask: true });
    try {
      const result = await loginByPassword({ phone, password });
      handleLoginResult(result, { phone, password });
    } catch (e) {
      /* toast 已在 request 中处理 */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  },

  goSms() {
    wx.navigateTo({ url: '/pages/sms-login/sms-login' });
  }
});
