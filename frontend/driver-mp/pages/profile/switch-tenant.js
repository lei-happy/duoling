const { ensureAuth } = require('../../utils/auth');
const { getUserTenants, switchTenant } = require('../../api/auth');
const { applyLoginSuccess, getUserInfo, getTenantCode } = require('../../services/session');
const { toast } = require('../../utils/request');

function pickTenants(list) {
  return (list || []).map((t) => ({
    tenantCode: t.tenantCode || t.tenant_code || '',
    tenantName: t.tenantName || t.tenant_name || ''
  }));
}

Page({
  data: {
    tenants: [],
    currentCode: '',
    currentName: '',
    loading: false
  },

  onShow() {
    if (!ensureAuth({})) return;
    const user = getUserInfo() || {};
    this.setData({
      currentCode: getTenantCode() || user.tenantCode || '',
      currentName: user.tenantName || ''
    });
    this.loadTenants();
  },

  async loadTenants() {
    this.setData({ loading: true });
    try {
      const list = await getUserTenants();
      this.setData({ tenants: pickTenants(list) });
    } catch (e) {
      /* handled */
    } finally {
      this.setData({ loading: false });
    }
  },

  async onSelect(e) {
    const tenantCode = e.currentTarget.dataset.code;
    if (!tenantCode || tenantCode === this.data.currentCode || this.data.loading) return;
    this.setData({ loading: true });
    wx.showLoading({ title: '正在切换企业，请稍候…', mask: true });
    try {
      const result = await switchTenant(tenantCode);
      applyLoginSuccess(result);
      toast('已切换企业');
      setTimeout(() => {
        wx.switchTab({ url: '/pages/home/index' });
      }, 400);
    } catch (err) {
      /* handled */
    } finally {
      wx.hideLoading();
      this.setData({ loading: false });
    }
  }
});
