const { ensureAuth } = require('../../utils/auth');
const { kpiSummary, revenueTrend, customerRank } = require('../../api/insight');
const { wan, listOf } = require('../../utils/format');

Page({
  data: { kpi: {}, trend: [], rank: [], loading: false },
  onShow() {
    if (!ensureAuth()) return;
    this.reload();
  },
  onPullDownRefresh() {
    this.reload().finally(() => wx.stopPullDownRefresh());
  },
  async reload() {
    this.setData({ loading: true });
    try {
      const [kpi, trend, rank] = await Promise.all([
        kpiSummary(),
        revenueTrend({ granularity: 'day' }),
        customerRank({ limit: 5 })
      ]);
      this.setData({
        kpi: {
          revenueWan: wan((kpi.revenue && kpi.revenue.todayValue) || 0),
          waybills: (kpi.waybillCount && kpi.waybillCount.todayValue) || 0,
          vehicles: (kpi.vehicleQuantity && kpi.vehicleQuantity.todayValue) || 0,
          customers: (kpi.customerCount && kpi.customerCount.todayValue) || 0,
          wow: kpi.revenue && kpi.revenue.weekOverWeekRate
        },
        trend: trend || [],
        rank: listOf(rank).map((x) => {
          const share = x.share != null ? Number(x.share) : null;
          return {
            ...x,
            shareText: share != null && Number.isFinite(share) ? `${(share * 100).toFixed(1)}%` : ''
          };
        })
      });
    } catch (e) { /* toast */ }
    finally { this.setData({ loading: false }); }
  },
  goOps() {
    wx.navigateTo({ url: '/pages/insight/ops' });
  }
});
