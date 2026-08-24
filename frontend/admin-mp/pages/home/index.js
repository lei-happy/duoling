const { ensureAuth } = require('../../utils/auth');
const { STORAGE_KEYS, getItem } = require('../../utils/storage');
const { PERSONA_OPTIONS, personaLabel, resolvePersona } = require('../../utils/persona');
const { saveDefaultPersona, canSeeFinance } = require('../../api/auth');
const { homeSummary } = require('../../api/workbench');
const { toast } = require('../../utils/request');
const { greet } = require('../../utils/format');

Page({
  data: {
    realName: '管理员',
    tenantName: '',
    currentPersona: '',
    switchers: [],
    showSwitcher: false,
    kpis: [],
    notice: '',
    primary: null,
    inboxCount: 0,
    canSeeAmount: true,
    emptyHint: '',
    loading: false,
    statusBarHeight: 20
  },

  onLoad() {
    const sys = wx.getSystemInfoSync();
    this.setData({ statusBarHeight: sys.statusBarHeight || 20 });
  },

  onShow() {
    if (!ensureAuth()) return;
    this.refresh();
  },

  onPullDownRefresh() {
    this.refresh().finally(() => wx.stopPullDownRefresh());
  },

  async refresh() {
    const user = getItem(STORAGE_KEYS.USER_INFO, null) || getApp().globalData.userInfo || {};
    const personas = user.personas || [];
    const current = resolvePersona(user);
    const switchers = PERSONA_OPTIONS.filter((x) => personas.indexOf(x.value) >= 0).map((x) => ({
      ...x,
      selected: x.value === current
    }));
    const financeOk = canSeeFinance(user);
    this.setData({
      realName: user.realName || user.nickname || '管理员',
      tenantName: user.tenantName || '',
      currentPersona: current,
      switchers,
      showSwitcher: switchers.length > 1,
      greet: greet(),
      canSeeAmount: current !== 'finance' || financeOk,
      emptyHint: personas.length ? '' : '请让管理员在「组织管理 → 角色」里补上岗位视图。'
    });
    if (!current) return;
    if (current === 'finance' && !financeOk) {
      this.setData({
        kpis: [],
        notice: '',
        primary: null,
        emptyHint: '没有资金权限，金额不会显示。请在电脑端找管理员开通。'
      });
      return;
    }
    this.setData({ loading: true });
    try {
      const data = await homeSummary(current);
      this.setData({
        kpis: data.kpis || [],
        notice: data.notice || '',
        primary: data.primaryAction || null,
        inboxCount: data.inboxCount || 0
      });
      const app = getApp();
      if (app) app.globalData.inboxCount = data.inboxCount || 0;
    } catch (e) {
      /* toast 已处理 */
    } finally {
      this.setData({ loading: false });
    }
  },

  async onSwitch(e) {
    const persona = e.currentTarget.dataset.persona;
    if (!persona || persona === this.data.currentPersona) return;
    try {
      await saveDefaultPersona(persona);
      this.refresh();
    } catch (e) {
      toast('切换视图失败，请重试');
    }
  },

  onBell() {
    wx.switchTab({ url: '/pages/message/index' });
  },

  onOrg() {
    wx.navigateTo({ url: '/pages/profile/switch-tenant' });
  },

  onPrimary() {
    const p = this.data.primary;
    if (!p || !p.path) return;
    if (p.path.indexOf('/pages/dispatch/index') === 0 || p.path.indexOf('/pages/insight/index') === 0) {
      wx.switchTab({ url: p.path.split('?')[0] });
      return;
    }
    wx.navigateTo({ url: p.path });
  },

  goDispatch() { wx.switchTab({ url: '/pages/dispatch/index' }); },
  goPlan() { wx.navigateTo({ url: '/pages/plan/index' }); },
  goTrack() { wx.navigateTo({ url: '/pages/track/index' }); },
  goReceipt() { wx.navigateTo({ url: '/pages/receipt/index' }); },
  goFee() { wx.navigateTo({ url: '/pages/fee/index' }); },
  goApproval() { wx.navigateTo({ url: '/pages/approval/index' }); },
  goInsight() { wx.switchTab({ url: '/pages/insight/index' }); },
  goLookup() { wx.navigateTo({ url: '/pages/lookup/index' }); }
});
