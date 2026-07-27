const { ensureAuth } = require('../../utils/auth');
const { getUserInfo, getTenantCode } = require('../../services/session');
const { listMyTasks } = require('../../api/task');
const { getFinanceSummary } = require('../../api/finance');
const { formatMoney } = require('../../utils/format');

Page({
  data: {
    realName: '司机',
    tenantName: '',
    avatarText: '司',
    kpi: { waitLoad: 0, inTransit: 0, waitSign: 0 },
    monthlyIncomeText: '0.00',
    recent: [],
    loading: false
  },

  onShow() {
    if (!ensureAuth({})) return;
    const user = getUserInfo() || {};
    const name = user.realName || '司机';
    this.setData({
      realName: name,
      tenantName: user.tenantName || getTenantCode() || '未选择企业',
      avatarText: name.slice(0, 1)
    });
    this.load();
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh());
  },

  async load() {
    if (this.data.loading) return;
    this.setData({ loading: true });
    try {
      const [r1, r2, r3, r4, summary] = await Promise.all([
        listMyTasks({ status: 1, page: 1, pageSize: 1 }),
        listMyTasks({ status: 3, page: 1, pageSize: 1 }),
        listMyTasks({ status: 4, page: 1, pageSize: 1 }),
        listMyTasks({ page: 1, pageSize: 5 }),
        getFinanceSummary().catch(() => ({ totalIncome: 0 }))
      ]);
      this.setData({
        kpi: {
          waitLoad: (r1 && r1.total) || 0,
          inTransit: (r2 && r2.total) || 0,
          waitSign: (r3 && r3.total) || 0
        },
        monthlyIncomeText: formatMoney(summary && summary.totalIncome),
        recent: (r4 && r4.list) || []
      });
    } catch (e) {
      /* handled */
    } finally {
      this.setData({ loading: false });
    }
  },

  goTask(e) {
    const dataset = (e && e.currentTarget && e.currentTarget.dataset) || {};
    const status = dataset.status;
    const app = getApp();
    if (app) {
      app.globalData.taskStatusFilter =
        status === undefined || status === null ? '' : String(status);
    }
    wx.switchTab({ url: '/pages/task/list' });
  },

  goTaskAll() {
    const app = getApp();
    if (app) app.globalData.taskStatusFilter = '';
    wx.switchTab({ url: '/pages/task/list' });
  },

  goFinance() {
    wx.switchTab({ url: '/pages/finance/list' });
  },

  goSummary() {
    wx.navigateTo({ url: '/pages/finance/summary' });
  },

  goProfile() {
    wx.switchTab({ url: '/pages/profile/index' });
  },

  goSwitchTenant() {
    wx.navigateTo({ url: '/pages/profile/switch-tenant' });
  },

  onTaskTap(e) {
    const id = e.detail.id;
    if (id) wx.navigateTo({ url: `/pages/task/detail?id=${id}` });
  }
});
