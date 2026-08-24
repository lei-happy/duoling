const { STORAGE_KEYS, getItem, removeItem } = require('../../utils/storage');
const { loginByPassword, loginBySms, finishLogin, isMultiTenant } = require('../../api/auth');
const { toast } = require('../../utils/request');

Page({
  data: { tenants: [], picked: '', loading: false },

  onShow() {
    const tenants = getItem(STORAGE_KEYS.PENDING_TENANTS, []) || [];
    this.setData({
      tenants,
      picked: (tenants[0] && tenants[0].tenantCode) || ''
    });
  },

  onPick(e) {
    this.setData({ picked: e.currentTarget.dataset.code });
  },

  async onEnter() {
    const { picked, loading } = this.data;
    if (!picked || loading) return;
    const pending = getItem(STORAGE_KEYS.PENDING_LOGIN, {}) || {};
    this.setData({ loading: true });
    wx.showLoading({ title: '正在进入，请稍候…', mask: true });
    try {
      const result =
        pending.mode === 'sms'
          ? await loginBySms({ phone: pending.phone, code: pending.code, tenantCode: picked })
          : await loginByPassword({
              phone: pending.phone,
              password: pending.password,
              tenantCode: picked
            });
      if (isMultiTenant(result)) {
        toast('请再选一次要进入的企业');
        return;
      }
      removeItem(STORAGE_KEYS.PENDING_LOGIN);
      removeItem(STORAGE_KEYS.PENDING_TENANTS);
      await finishLogin(result);
    } catch (e) {
      /* toast 已处理 */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  }
});
