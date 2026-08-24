const { ensureAuth } = require('../../utils/auth');
const { listWaybills, confirmReceipt, revokeReceipt, listReceipts } = require('../../api/waybill');
const { listOf, routeText } = require('../../utils/format');
const { toast } = require('../../utils/request');

Page({
  data: { tab: 0, list: [] },
  onShow() {
    if (!ensureAuth()) return;
    this.reload();
  },
  onPullDownRefresh() {
    this.reload().finally(() => wx.stopPullDownRefresh());
  },
  onTab(e) {
    this.setData({ tab: Number(e.currentTarget.dataset.tab) });
    this.reload();
  },
  async reload() {
    const status = this.data.tab === 0 ? 5 : 6;
    const page = await listWaybills({ status });
    const rows = listOf(page);
    const list = [];
    for (const w of rows) {
      let thumbs = [];
      try {
        const recs = await listReceipts(w.id);
        const first = listOf(recs)[0] || recs[0];
        thumbs = (first && first.fileUrls) || [];
      } catch (e) { thumbs = []; }
      list.push({
        id: w.id,
        no: w.waybillNo,
        route: routeText(w.origin, w.destination),
        qty: w.quantity,
        thumbs,
        mockFlag: thumbs.length === 0 && this.data.tab === 0 ? '待人工看图' : ''
      });
    }
    this.setData({ list });
  },
  onReview(e) {
    wx.navigateTo({ url: `/pages/receipt/review?id=${e.currentTarget.dataset.id}&tab=${this.data.tab}` });
  },
  async onConfirm(e) {
    wx.showLoading({ title: '正在确认回单，请稍候…', mask: true });
    try {
      await confirmReceipt(e.currentTarget.dataset.id, { fileUrls: [], fileType: 1 });
      toast('回单已确认');
      this.reload();
    } catch (err) { /* toast */ }
    finally { wx.hideLoading(); }
  },
  async onRevoke(e) {
    wx.showLoading({ title: '正在撤销，请稍候…', mask: true });
    try {
      await revokeReceipt(e.currentTarget.dataset.id);
      toast('已撤销回单');
      this.reload();
    } catch (err) { /* toast */ }
    finally { wx.hideLoading(); }
  }
});
