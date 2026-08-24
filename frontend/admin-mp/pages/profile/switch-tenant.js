const { ensureAuth } = require('../../utils/auth');
const { STORAGE_KEYS, getItem } = require('../../utils/storage');
const { listTenants, switchTenant, goAfterLogin } = require('../../api/auth');
const { listOf } = require('../../utils/format');
const { toast } = require('../../utils/request');

Page({
  data: { tenants: [], picked: '', current: '', loading: false },

  onShow() {
    if (!ensureAuth()) return;
    this.load();
  },

  async load() {
    const user = getItem(STORAGE_KEYS.USER_INFO, {}) || {};
    const current = user.tenantCode || getItem(STORAGE_KEYS.TENANT_CODE, '') || '';
    try {
      const raw = await listTenants();
      const tenants = Array.isArray(raw) ? raw : listOf(raw);
      this.setData({
        tenants,
        current,
        picked: current || (tenants[0] && tenants[0].tenantCode) || ''
      });
    } catch (e) {
      /* toast 已处理 */
    }
  },

  onPick(e) {
    this.setData({ picked: e.currentTarget.dataset.code });
  },

  async onEnter() {
    const { picked, current, loading } = this.data;
    if (!picked || loading) return;
    if (picked === current) {
      wx.navigateBack();
      return;
    }
    this.setData({ loading: true });
    wx.showLoading({ title: '正在切换企业，请稍候…', mask: true });
    try {
      const user = await switchTenant(picked);
      toast('已进入新企业');
      goAfterLogin(user);
    } catch (e) {
      /* toast 已处理 */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  }
});
