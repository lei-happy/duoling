const { ensureAuth } = require('../../utils/auth');
const { getMyFundAccount, listMyFundTransactions } = require('../../api/finance');
const { fundBizTypeLabel } = require('../../utils/constants');
const { formatDateTime, formatMoney } = require('../../utils/format');
const { getFontScale } = require('../../utils/font');

Page({
  data: {
    fontClass: 'font-lg',
    balanceText: '0.00',
    totalInText: '0.00',
    totalOutText: '0.00',
    frozenText: '0.00',
    list: [],
    page: 1,
    pageSize: 20,
    loading: false,
    loadingMore: false,
    finished: false
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.loadAccount();
    this.reload();
  },

  onPullDownRefresh() {
    Promise.all([this.loadAccount(), this.reload()]).finally(() => wx.stopPullDownRefresh());
  },

  onReachBottom() {
    this.loadMore();
  },

  async loadAccount() {
    try {
      const acc = await getMyFundAccount();
      this.setData({
        balanceText: formatMoney(acc.balance),
        totalInText: formatMoney(acc.totalIn),
        totalOutText: formatMoney(acc.totalOut),
        frozenText: formatMoney(acc.frozenAmount)
      });
    } catch (e) {
      /* handled */
    }
  },

  async reload() {
    this.setData({ page: 1, finished: false, list: [] });
    await this.fetch(true);
  },

  async loadMore() {
    if (this.data.finished || this.data.loading || this.data.loadingMore) return;
    this.setData({ page: this.data.page + 1 });
    await this.fetch(false);
  },

  async fetch(reset) {
    if (reset) this.setData({ loading: true });
    else this.setData({ loadingMore: true });
    try {
      const res = await listMyFundTransactions({
        page: this.data.page,
        pageSize: this.data.pageSize
      });
      const raw = (res && res.list) || [];
      const mapped = raw.map((t) => {
        const sign = t.direction === 1 ? '+' : '-';
        return {
          ...t,
          bizLabel: fundBizTypeLabel(t.bizType),
          deltaText: `${sign}¥${formatMoney(t.amount)}`,
          balanceText: formatMoney(t.balanceAfter),
          timeText: formatDateTime(t.createdAt)
        };
      });
      const total = (res && res.total) || 0;
      const merged = reset ? mapped : this.data.list.concat(mapped);
      this.setData({
        list: merged,
        finished: merged.length >= total || mapped.length === 0
      });
    } catch (e) {
      if (!reset) this.setData({ page: Math.max(1, this.data.page - 1) });
    } finally {
      this.setData({ loading: false, loadingMore: false });
    }
  }
});
