const { ensureAuth } = require('../../utils/auth');
const { listMyFinance, getFinanceSummary } = require('../../api/finance');
const { FINANCE_DOC_TYPE, FINANCE_STATUS } = require('../../utils/constants');
const { formatDate, formatMoney } = require('../../utils/format');

const tabs = [
  { title: '全部', name: 'all' },
  ...Object.keys(FINANCE_DOC_TYPE).map((k) => ({
    title: FINANCE_DOC_TYPE[k],
    name: String(k)
  }))
];

function toApiDocType(tabValue) {
  return !tabValue || tabValue === 'all' ? '' : String(tabValue);
}

Page({
  data: {
    tabs,
    docType: 'all',
    list: [],
    page: 1,
    pageSize: 15,
    loading: false,
    loadingMore: false,
    finished: false,
    totalIncomeText: '0.00',
    prepaidText: '0.00',
    supplementText: '0.00',
    settledText: '0.00',
    taskId: ''
  },

  onLoad(query) {
    if (query.taskId) this.setData({ taskId: query.taskId });
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.loadSummary();
    this.reload();
  },

  onPullDownRefresh() {
    Promise.all([this.loadSummary(), this.reload()]).finally(() => wx.stopPullDownRefresh());
  },

  onReachBottom() {
    this.loadMore();
  },

  async loadSummary() {
    try {
      const s = await getFinanceSummary();
      this.setData({
        totalIncomeText: formatMoney(s.totalIncome),
        prepaidText: formatMoney(s.prepaidAmount),
        supplementText: formatMoney(s.supplementAmount),
        settledText: formatMoney(s.settledAmount)
      });
    } catch (e) {
      /* handled */
    }
  },

  onTabsChange(e) {
    const name = e.detail && e.detail.value;
    const next = name == null || name === '' ? 'all' : String(name);
    if (next === this.data.docType) return;
    this.setData({ docType: next });
    this.reload();
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
      const params = { page: this.data.page, pageSize: this.data.pageSize };
      const docType = toApiDocType(this.data.docType);
      if (docType !== '') params.docType = Number(docType);
      const res = await listMyFinance(params);
      const raw = (res && res.list) || [];
      const mapped = raw.map((d) => {
        const st = FINANCE_STATUS[d.status] || { label: '未知', level: 'default' };
        return {
          ...d,
          statusLabel: st.label,
          statusLevel: st.level,
          typeLabel: FINANCE_DOC_TYPE[d.docType] || '费用单',
          amountText: formatMoney(d.actualAmount != null ? d.actualAmount : d.plannedAmount),
          timeText: formatDate(d.actualPayTime || d.plannedPayTime)
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
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/finance/detail?id=${id}` });
  },

  goFundAccount() {
    wx.navigateTo({ url: '/pages/finance/fund-account' });
  }
});
