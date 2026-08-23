const { ensureAuth } = require('../../utils/auth');
const { getFinanceSummary } = require('../../api/finance');
const { formatMoney } = require('../../utils/format');
const { getFontScale } = require('../../utils/font');

Page({
  data: {
    fontClass: 'font-lg',
    totalIncomeText: '0.00',
    avgMonthText: '0.00',
    bars: []
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.load();
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh());
  },

  async load() {
    try {
      const summary = await getFinanceSummary();
      const byMonth = summary.byMonth || [];
      const max = Math.max(1, ...byMonth.map((m) => Number(m.amount) || 0));
      const now = new Date();
      const cur = `${now.getFullYear()}-${`${now.getMonth() + 1}`.padStart(2, '0')}`;
      const avg = byMonth.length
        ? (byMonth.reduce((s, m) => s + Number(m.amount || 0), 0) / byMonth.length)
        : 0;
      this.setData({
        totalIncomeText: formatMoney(summary.totalIncome),
        avgMonthText: formatMoney(avg),
        bars: byMonth.slice(-6).map((m) => ({
          month: m.month,
          label: (m.month || '').slice(5),
          shortAmount: formatMoney(m.amount, 0),
          h: Math.max(8, Math.round((Number(m.amount) || 0) / max * 100)),
          hi: m.month === cur
        }))
      });
    } catch (e) {
      /* handled */
    }
  }
});
