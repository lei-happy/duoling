const { ensureAuth } = require('../../utils/auth');
const { lookup } = require('../../api/workbench');
const { toast } = require('../../utils/request');

const TYPE_LABEL = { customer: '客户', carrier: '承运商', capacity: '运力' };

Page({
  data: { keyword: '', items: [], recent: [] },
  onShow() {
    if (!ensureAuth()) return;
    this.setData({ recent: wx.getStorageSync('admin_mp_lookup_recent') || [] });
  },
  onInput(e) {
    this.setData({ keyword: (e.detail.value || '').trim() });
  },
  async onSearch() {
    const kw = this.data.keyword;
    if (!kw) return;
    try {
      const data = await lookup(kw);
      const items = ((data && data.items) || []).map((x) => ({
        ...x,
        typeLabel: TYPE_LABEL[x.type] || x.type
      }));
      this.setData({ items });
    } catch (e) { /* toast */ }
  },
  onCall(e) {
    const phone = e.currentTarget.dataset.phone;
    if (!phone) {
      toast('没有电话');
      return;
    }
    wx.makePhoneCall({ phoneNumber: String(phone) });
  },
  onOpen(e) {
    const source = this.data.items.length ? this.data.items : this.data.recent;
    const item = source[e.currentTarget.dataset.idx];
    if (!item) return;
    const recent = [item, ...this.data.recent.filter((x) => x.id !== item.id)].slice(0, 8);
    wx.setStorageSync('admin_mp_lookup_recent', recent);
    wx.navigateTo({
      url: `/pages/lookup/card?type=${item.type}&id=${item.id}&title=${encodeURIComponent(item.title)}&phone=${item.phone || ''}&subtitle=${encodeURIComponent(item.subtitle || '')}`
    });
  }
});
