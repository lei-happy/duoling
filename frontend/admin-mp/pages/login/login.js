const { ensureAuth } = require('../../utils/auth');
const { loginByPassword, completeLogin, isMultiTenant } = require('../../api/auth');
const { toast } = require('../../utils/request');

Page({
  data: {
    phone: '',
    password: '',
    loading: false,
    tenants: [],
    selectingTenant: false
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
    await this.doLogin();
  },

  async onPickTenant(e) {
    const tenantCode = e.currentTarget.dataset.code;
    if (!tenantCode || this.data.loading) return;
    await this.doLogin(tenantCode);
  },

  async doLogin(tenantCode) {
    const { phone, password } = this.data;
    this.setData({ loading: true });
    wx.showLoading({ title: '正在进入，请稍候…', mask: true });
    try {
      const result = await loginByPassword({ phone, password, tenantCode });
      if (isMultiTenant(result)) {
        this.setData({
          tenants: result.tenants || [],
          selectingTenant: true
        });
        return;
      }
      await completeLogin(result);
      wx.switchTab({ url: '/pages/home/index' });
    } catch (e) {
      /* toast 已处理 */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  }
});
