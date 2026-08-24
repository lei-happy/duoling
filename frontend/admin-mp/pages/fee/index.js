const { ensureAuth } = require('../../utils/auth');
const { STORAGE_KEYS, getItem } = require('../../utils/storage');
const { canSeeFinance } = require('../../api/auth');
const { listDocs, financeStats } = require('../../api/finance');
const { listOf, money, wan, shortTime } = require('../../utils/format');

Page({
  data: { allowed: true, tab: 2, list: [], amounts: {}, totals: {}, pendingPayWan: '0.0' },
  onShow() {
    if (!ensureAuth()) return;
    const user = getItem(STORAGE_KEYS.USER_INFO, {}) || {};
    const allowed = canSeeFinance(user);
    this.setData({ allowed });
    if (allowed) this.reload();
  },
  onPullDownRefresh() {
    this.reload().finally(() => wx.stopPullDownRefresh());
  },
  onTab(e) {
    this.setData({ tab: Number(e.currentTarget.dataset.tab) });
    this.reload();
  },
  async reload() {
    try {
      const [stats, page] = await Promise.all([
        financeStats(),
        listDocs({ status: this.data.tab })
      ]);
      const amounts = (stats && stats.amounts) || {};
      this.setData({
        totals: (stats && stats.totals) || {},
        amounts,
        pendingPayWan: wan(amounts.pendingPayAmount),
        list: listOf(page).map((d) => ({
          ...d,
          amountText: money(d.plannedAmount, 0),
          time: shortTime(d.plannedPayTime)
        }))
      });
    } catch (e) { /* toast */ }
  },
  onItem(e) {
    wx.navigateTo({ url: `/pages/fee/detail?id=${e.currentTarget.dataset.id}` });
  }
});
