const { ensureAuth } = require('../../utils/auth');
const { listMyFinance } = require('../../api/finance');
const { FINANCE_DOC_TYPE, FINANCE_STATUS, PAY_METHOD } = require('../../utils/constants');
const { formatDate, formatMoney } = require('../../utils/format');
const { getFontScale } = require('../../utils/font');

function mapDoc(d) {
  const st = FINANCE_STATUS[d.status] || { label: '未知', level: 'default' };
  const paid = d.status === 3;
  const revoked = d.status === 4;
  return {
    id: d.id,
    icon: paid ? 'check' : revoked ? 'info' : 'clock',
    tone: paid ? 'green' : revoked ? '' : 'amber',
    title: `${FINANCE_DOC_TYPE[d.docType] || '费用单'} · ${d.taskNo || d.docNo}`,
    subtitle: `${formatDate(d.actualPayTime || d.plannedPayTime)} · ${PAY_METHOD[d.payMethod] || st.label}`,
    amountText: `${paid ? '+' : ''}${formatMoney(d.actualAmount != null ? d.actualAmount : d.plannedAmount)}`,
    extraTone: paid ? 'ok' : revoked ? 'dim' : ''
  };
}

Page({
  data: {
    fontClass: 'font-lg',
    chips: [
      { label: '全部', value: 'all' },
      { label: '预付单', value: '1' },
      { label: '补款单', value: '2' },
      { label: '结算单', value: '3' }
    ],
    docType: 'all',
    list: [],
    page: 1,
    pageSize: 15,
    loading: false,
    loadingMore: false,
    finished: false
  },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.reload();
  },

  onPullDownRefresh() {
    this.reload().finally(() => wx.stopPullDownRefresh());
  },

  onReachBottom() {
    this.loadMore();
  },

  onTabsChange(e) {
    const next = (e.detail && e.detail.value) || 'all';
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
      if (this.data.docType !== 'all') params.docType = Number(this.data.docType);
      const res = await listMyFinance(params);
      const mapped = ((res && res.list) || []).map(mapDoc);
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
  }
});
