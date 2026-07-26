const { loginByPassword, loginBySms } = require('../../api/auth');
const {
  loadPendingLogin,
  applyLoginSuccess,
  navigateAfterLogin,
  isMultiTenant
} = require('../../services/session');
const { STORAGE_KEYS, getItem } = require('../../utils/storage');
const { toast } = require('../../utils/request');

Page({
  data: {
    tenants: [],
    loading: false
  },

  onShow() {
    const app = getApp();
    const pending = loadPendingLogin();
    const tenants = (app && app.globalData.pendingTenants) || [];
    this.setData({ tenants });

    // 多企业第一步：有 pending 即可；否则需已登录（不应进此页）
    if (!pending && !getItem(STORAGE_KEYS.ACCESS_TOKEN, '')) {
      wx.reLaunch({ url: '/pages/login/login' });
      return;
    }
    if (!tenants.length) {
      toast('请重新登录后再选择企业');
      setTimeout(() => wx.reLaunch({ url: '/pages/login/login' }), 800);
    }
  },

  async onSelect(e) {
    const tenantCode = e.currentTarget.dataset.code;
    const pending = loadPendingLogin();
    if (!pending) {
      toast('登录信息已失效，请重新登录');
      wx.reLaunch({ url: '/pages/login/login' });
      return;
    }
    if (this.data.loading) return;
    this.setData({ loading: true });
    wx.showLoading({ title: '正在进入企业，请稍候…', mask: true });
    try {
      let result;
      if (pending.password) {
        result = await loginByPassword({
          phone: pending.phone,
          password: pending.password,
          tenantCode
        });
      } else {
        result = await loginBySms({
          phone: pending.phone,
          code: pending.code,
          tenantCode
        });
      }
      if (isMultiTenant(result)) {
        toast('请选择具体企业');
        return;
      }
      applyLoginSuccess(result);
      navigateAfterLogin(result.user);
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  }
});
