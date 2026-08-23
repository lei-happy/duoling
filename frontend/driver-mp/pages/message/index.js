const { ensureAuth } = require('../../utils/auth');
const { getFontScale } = require('../../utils/font');
const { listMessages, markRead, removeMessage } = require('../../services/mock/message');

Page({
  data: { fontClass: 'font-lg', tab: 'all', list: [] },

  onShow() {
    if (!ensureAuth({})) return;
    this.setData({ fontClass: getFontScale().className });
    this.reload();
  },

  setTab(e) {
    this.setData({ tab: e.currentTarget.dataset.v });
    this.reload();
  },

  reload() {
    const tab = this.data.tab;
    let list = listMessages();
    if (tab !== 'all') list = list.filter((m) => m.kind === tab);
    this.setData({ list });
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    markRead(id);
    wx.navigateTo({ url: `/pages/message/detail?id=${id}` });
  },

  onRead(e) {
    markRead(e.currentTarget.dataset.id);
    this.reload();
  },

  onDel(e) {
    removeMessage(e.currentTarget.dataset.id);
    this.reload();
  },

  onTouchStart(e) {
    this._sx = e.touches[0].clientX;
    this._id = e.currentTarget.dataset.id;
  },

  onTouchMove(e) {
    if (this._sx == null) return;
    const dx = Math.min(0, Math.max(-120, e.touches[0].clientX - this._sx));
    this.patch(this._id, dx);
  },

  onTouchEnd() {
    const id = this._id;
    const cur = (this.data.list.find((m) => m.id === id) || {}).offset || 0;
    this.patch(id, cur < -60 ? -120 : 0);
    this._sx = null;
    this._id = null;
  },

  patch(id, offset) {
    this.setData({
      list: this.data.list.map((m) => (m.id === id ? { ...m, offset } : { ...m, offset: 0 }))
    });
  }
});
