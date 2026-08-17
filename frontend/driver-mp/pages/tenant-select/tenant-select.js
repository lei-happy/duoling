const { loginByPassword, loginBySms } = require('../../api/auth');
const {
  loadPendingLogin,
  applyLoginSuccess,
  navigateAfterLogin,
  isMultiTenant
} = require('../../services/session');
const { STORAGE_KEYS, getItem } = require('../../utils/storage');
const { toast } = require('../../utils/request');

const LOGO_BGS = [
  'linear-gradient(145deg,#2f5fe0,#1d4ed8)',
  'linear-gradient(145deg,#0ea5e9,#0369a1)',
  'linear-gradient(145deg,#f5a524,#c97c00)',
  'linear-gradient(145deg,#16a34a,#15803d)'
];

function decorateTenants(list) {
  return (list || []).map((t, i) => {
    const name = t.tenantName || t.tenantCode || '';
    return {
      ...t,
      initial: name.slice(0, 1) || '企',
      logoBg: LOGO_BGS[i % LOGO_BGS.length]
    };
  });
}

function enterLabel(tenants, selectedCode) {
  const hit = (tenants || []).find((t) => t.tenantCode === selectedCode);
  if (!hit) return '';
  const name = hit.tenantName || hit.tenantCode;
  return name.length > 10 ? `进入${name.slice(0, 10)}…` : `进入${name}`;
}

Page({
  data: {
    tenants: [],
    selectedCode: '',
    enterLabel: '',
    loading: false
  },

  onShow() {
    const app = getApp();
    const pending = loadPendingLogin();
    const tenants = decorateTenants((app && app.globalData.pendingTenants) || []);
    const selectedCode = (tenants[0] && tenants[0].tenantCode) || '';
    this.setData({
      tenants,
      selectedCode,
      enterLabel: enterLabel(tenants, selectedCode)
    });

    if (!pending && !getItem(STORAGE_KEYS.ACCESS_TOKEN, '')) {
      wx.reLaunch({ url: '/pages/login/login' });
      return;
    }
    if (!tenants.length) {
      toast('请重新登录后再选择企业');
      setTimeout(() => wx.reLaunch({ url: '/pages/login/login' }), 800);
    }
  },

  onPick(e) {
    const selectedCode = e.currentTarget.dataset.code;
    if (!selectedCode || this.data.loading) return;
    this.setData({
      selectedCode,
      enterLabel: enterLabel(this.data.tenants, selectedCode)
    });
  },

  async onEnter() {
    const tenantCode = this.data.selectedCode;
    const pending = loadPendingLogin();
    if (!pending) {
      toast('登录信息已失效，请重新登录');
      wx.reLaunch({ url: '/pages/login/login' });
      return;
    }
    if (!tenantCode) {
      toast('请先选择要进入的企业');
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
