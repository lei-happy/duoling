const { ensureAuth } = require('../../utils/auth');
const { listWaybills, waybillStats, updateStatus, batchStatus } = require('../../api/waybill');
const { listOf, routeText, shortTime } = require('../../utils/format');
const { toast } = require('../../utils/request');

function mapRow(item) {
  const issues = [];
  if (item.freightAmount == null) issues.push('运价缺失');
  return {
    id: item.id,
    no: item.waybillNo,
    route: routeText(item.origin, item.destination),
    qty: item.quantity,
    customer: item.customerName || '',
    time: shortTime(item.requiredDeliverTime),
    issues,
    blocked: issues.length > 0
  };
}

Page({
  data: { tab: 0, counts: {}, list: [], pickMode: false, picked: {}, pickCount: 0 },

  onShow() {
    if (!ensureAuth()) return;
    this.reload();
  },
  onPullDownRefresh() {
    this.reload().finally(() => wx.stopPullDownRefresh());
  },

  async reload() {
    const status = this.data.tab === 0 ? 0 : this.data.tab === 1 ? 1 : undefined;
    try {
      const [stats, page] = await Promise.all([
        waybillStats(),
        listWaybills({ status })
      ]);
      const totals = (stats && stats.totals) || {};
      this.setData({
        counts: { pending: totals.pendingConfirm || totals[0] || 0, confirmed: totals.pendingDispatch || 0 },
        list: listOf(page).map(mapRow)
      });
    } catch (e) { /* toast */ }
  },

  onTab(e) {
    this.setData({ tab: Number(e.currentTarget.dataset.tab), pickMode: false, picked: {}, pickCount: 0 });
    this.reload();
  },

  togglePick() {
    this.setData({ pickMode: !this.data.pickMode, picked: {}, pickCount: 0 });
  },

  onCheck(e) {
    const item = this.data.list.find((x) => x.id === e.currentTarget.dataset.id);
    if (item && item.blocked) {
      toast('有问题的计划不能批量确认，请点进去单独看');
      return;
    }
    const picked = { ...this.data.picked };
    const id = e.currentTarget.dataset.id;
    if (picked[id]) delete picked[id];
    else picked[id] = true;
    this.setData({ picked, pickCount: Object.keys(picked).length });
  },

  onItem(e) {
    if (this.data.pickMode) return this.onCheck(e);
    wx.navigateTo({ url: `/pages/plan/detail?id=${e.currentTarget.dataset.id}` });
  },

  async onBatch() {
    const ids = Object.keys(this.data.picked).map(Number);
    if (!ids.length) return;
    wx.showLoading({ title: '正在确认计划，请稍候…', mask: true });
    try {
      const res = await batchStatus(ids, 1);
      toast(`已确认 ${res.success || ids.length} 条计划`);
      this.setData({ pickMode: false, picked: {}, pickCount: 0 });
      this.reload();
    } catch (e) { /* toast */ }
    finally { wx.hideLoading(); }
  }
});
