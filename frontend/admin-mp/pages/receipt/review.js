const { ensureAuth } = require('../../utils/auth');
const { getWaybill, listReceipts, confirmReceipt } = require('../../api/waybill');
const { listOf } = require('../../utils/format');
const { toast } = require('../../utils/request');

Page({
  data: { item: null, urls: [], tab: 0 },
  onLoad(q) {
    this.id = q.id;
    this.setData({ tab: Number(q.tab || 0) });
    this.load();
  },
  async load() {
    if (!ensureAuth()) return;
    const [w, recs] = await Promise.all([getWaybill(this.id), listReceipts(this.id).catch(() => [])]);
    const first = listOf(recs)[0] || recs[0] || {};
    this.setData({ item: w, urls: first.fileUrls || [] });
  },
  preview(e) {
    wx.previewImage({ current: e.currentTarget.dataset.src, urls: this.data.urls });
  },
  async onConfirm() {
    await confirmReceipt(this.id, { fileUrls: this.data.urls, fileType: 1 });
    toast('回单已确认');
    wx.navigateBack();
  }
});
